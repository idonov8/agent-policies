#!/usr/bin/env python3
"""Install symlinks with backups; preserve credentials and hooks."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, os, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--home", type=Path, default=Path.home(), help="Explicit installation home (use a temporary directory to test).")
HOME = parser.parse_args().home.expanduser().resolve()
subprocess.run(['python3', str(ROOT / 'scripts/render.py'), '--check'], check=True)
backup = HOME / '.local/state/agent-policies/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup.mkdir(parents=True, mode=0o700)
os.chmod(backup, 0o700)
manifest = []
def save(path):
    record = {'path': str(path), 'existed': path.exists() or path.is_symlink()}
    if record['existed']:
        target = backup / str(len(manifest))
        if path.is_symlink():
            record['symlink'] = os.readlink(path)
        elif path.is_dir():
            shutil.copytree(path, target, symlinks=True)
            record['backup'] = str(target)
        else:
            shutil.copy2(path, target)
            record['backup'] = str(target)
    manifest.append(record)
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
def link(path, target):
    if path.is_symlink() and path.resolve() == target.resolve():
        return
    save(path)
    if path.is_dir() and not path.is_symlink():
        # Keep an original Git checkout intact, including local-only commits.
        archived = backup / f'original-{len(manifest) - 1}-{path.name}'
        path.rename(archived)
        manifest[-1]['moved_to'] = str(archived)
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    elif path.exists() or path.is_symlink():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(os.path.relpath(target, path.parent), target_is_directory=target.is_dir())
link(HOME / '.codex/AGENTS.md', ROOT / 'agents/codex.md')
link(HOME / '.gemini/GEMINI.md', ROOT / 'agents/gemini.md')
link(HOME / '.claude/CLAUDE.md', ROOT / 'global.md')
link(HOME / '.claude/rules', ROOT / 'claude-rules')
link(HOME / '.cursor/rules/global.mdc', ROOT / 'agents/cursor.mdc')
for skill_file in sorted((ROOT / 'skills').glob('*/SKILL.md')):
    skill = skill_file.parent
    if skill.name.startswith('.') or not skill_file.is_file():
        continue
    for directory in ('.agents/skills', '.claude/skills'):
        link(HOME / directory / skill.name, skill)
settings = HOME / '.gemini/settings.json'
config = json.loads(settings.read_text()) if settings.exists() else {}
context = config.setdefault('context', {})
names = context.get('fileName', ['GEMINI.md'])
if isinstance(names, str):
    names = [names]
updated = list(dict.fromkeys([*names, 'AGENTS.md']))
if context.get('fileName') != updated:
    save(settings)
    context['fileName'] = updated
    mode = settings.stat().st_mode & 0o777 if settings.exists() else 0o600
    settings.parent.mkdir(parents=True, exist_ok=True)
    temp = settings.with_name(settings.name + '.agent-policies.tmp')
    temp.write_text(json.dumps(config, indent=2) + '\n')
    temp.chmod(mode)
    os.replace(temp, settings)
print('Installed. Private backups: ' + str(backup))
