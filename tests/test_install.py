"""Exercise installation and backups without writing to the real home directory."""
from pathlib import Path
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATHS = ('.agents/skills', '.claude/skills')


class InstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve() / 'repo'
        self.home = Path(temporary.name).resolve() / 'home'
        self.home.mkdir()
        bin_dir = self.home / 'bin'
        bin_dir.mkdir()
        curl = bin_dir / 'curl'
        curl.write_text('#!/bin/sh\ncat "$SKILL_ARCHIVE"\n')
        curl.chmod(0o755)
        self.archive = self.home / 'upstream.tar.gz'
        self.env = {**os.environ, 'PATH': f'{bin_dir}{os.pathsep}{os.environ["PATH"]}',
                    'SKILL_ARCHIVE': str(self.archive)}
        self.write_upstream('initial')
        self.repo.mkdir()
        for directory in ('scripts', 'claude-rules', 'skills'):
            shutil.copytree(ROOT / directory, self.repo / directory)
        shutil.copy2(ROOT / 'global.md', self.repo / 'global.md')
        (self.repo / 'agents').mkdir()
        subprocess.run(
            [sys.executable, str(self.repo / 'scripts/render.py')],
            check=True, capture_output=True, text=True,
        )

    def write_upstream(self, version):
        with tarfile.open(self.archive, 'w:gz') as archive:
            for name, data in (
                ('SKILL.md', f'---\nname: i-have-adhd\n---\n{version}\n'.encode()),
                ('agents/openai.yaml', b'policy: {allow_implicit_invocation: false}\n'),
                ('agents/gemini.toml', b'description = "fixture"\n'),
            ):
                member = tarfile.TarInfo(f'i-have-adhd-main/skills/i-have-adhd/{name}')
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))

    def install(self):
        result = subprocess.run(
            [sys.executable, str(self.repo / 'scripts/install.py'),
             '--home', str(self.home)],
            capture_output=True, text=True, env=self.env,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        backup = Path(result.stdout.split('Private backups: ')[1].strip())
        manifest = backup / 'manifest.json'
        return json.loads(manifest.read_text()) if manifest.exists() else []

    def assert_skill_link(self, directory, name='example-workflow'):
        installed = self.home / directory / name
        self.assertTrue(installed.is_symlink())
        self.assertFalse(os.path.isabs(os.readlink(installed)))
        self.assertEqual(installed.resolve(), self.repo / 'skills' / name)
        self.assertTrue((installed / 'SKILL.md').is_file())

    def test_install_preserves_other_skills_and_settings_and_is_repeatable(self):
        for directory in SKILL_PATHS:
            other = self.home / directory / 'other-skill/SKILL.md'
            other.parent.mkdir(parents=True)
            other.write_text('Unrelated skill')
        settings = self.home / '.gemini/settings.json'
        settings.parent.mkdir()
        settings.write_text(json.dumps({'theme': 'custom', 'context': {'fileName': 'CUSTOM.md'}}))
        auth = self.home / '.codex/auth.json'
        auth.parent.mkdir()
        auth.write_text('existing credentials')
        helper = self.repo / 'skills/example-workflow/scripts/helper.txt'
        helper.parent.mkdir()
        helper.write_text('Bundled resource')
        for name in ('not-a-skill', '.hidden'):
            (self.repo / 'skills' / name).mkdir()
        (self.repo / 'skills/.hidden/SKILL.md').write_text('Hidden example')
        second = self.repo / 'skills/second-skill'
        second.mkdir()
        (second / 'SKILL.md').write_text('---\nname: second-skill\ndescription: Test fixture\n---\n')

        self.install()

        for directory in SKILL_PATHS:
            self.assert_skill_link(directory)
            self.assert_skill_link(directory, 'second-skill')
            self.assertEqual((self.home / directory / 'other-skill/SKILL.md').read_text(), 'Unrelated skill')
            self.assertEqual((self.home / directory / 'example-workflow/scripts/helper.txt').read_text(), 'Bundled resource')
            self.assertFalse((self.home / directory / 'not-a-skill').exists())
            self.assertFalse((self.home / directory / '.hidden').exists())
        expected = {'theme': 'custom', 'context': {'fileName': ['CUSTOM.md', 'AGENTS.md']}}
        self.assertEqual(json.loads(settings.read_text()), expected)
        self.assertEqual(auth.read_text(), 'existing credentials')
        self.assertEqual(self.install(), [])

    def test_upstream_skill_refreshes_and_survives_failed_download(self):
        self.install()
        paths = [self.home / directory / 'i-have-adhd' for directory in SKILL_PATHS]
        original = paths[0].resolve()

        self.write_upstream('updated')
        self.install()
        for path in paths:
            self.assertNotEqual(path.resolve(), original)
            self.assertIn('updated', (path / 'SKILL.md').read_text())

        self.archive.unlink()
        self.install()
        for path in paths:
            self.assertIn('updated', (path / 'SKILL.md').read_text())

    def test_same_named_directories_have_separate_recoverable_backups(self):
        originals = {}
        for directory in SKILL_PATHS:
            skill = self.home / directory / 'example-workflow'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text(directory)
            originals[str(skill)] = directory

        manifest = self.install()

        archives = set()
        for record in manifest:
            if record['path'] in originals:
                archived = Path(record['moved_to'])
                archives.add(archived)
                self.assertEqual((archived / 'SKILL.md').read_text(), originals[record['path']])
                self.assertEqual((Path(record['backup']) / 'SKILL.md').read_text(), originals[record['path']])
        self.assertEqual(len(archives), 2)
        for directory in SKILL_PATHS:
            self.assert_skill_link(directory)

    def test_conflicting_file_and_broken_symlink_are_recorded(self):
        existing_file = self.home / '.agents/skills/example-workflow'
        existing_file.parent.mkdir(parents=True)
        existing_file.write_text('Previous file')
        existing_link = self.home / '.claude/skills/example-workflow'
        existing_link.parent.mkdir(parents=True)
        existing_link.symlink_to('missing-skill')

        records = {record['path']: record for record in self.install()}

        self.assertEqual(Path(records[str(existing_file)]['backup']).read_text(), 'Previous file')
        self.assertEqual(records[str(existing_link)]['symlink'], 'missing-skill')
        self.assertTrue(records[str(existing_link)]['existed'])
        for directory in SKILL_PATHS:
            self.assert_skill_link(directory)

    def test_policy_installation_still_works_without_skills(self):
        shutil.rmtree(self.repo / 'skills')

        self.install()

        for location, target in (
            ('.codex/AGENTS.md', 'agents/codex.md'),
            ('.gemini/GEMINI.md', 'agents/gemini.md'),
            ('.claude/CLAUDE.md', 'global.md'),
            ('.claude/rules', 'claude-rules'),
            ('.cursor/rules/global.mdc', 'agents/cursor.mdc'),
        ):
            self.assertEqual((self.home / location).resolve(), self.repo / target)


if __name__ == '__main__':
    unittest.main()
