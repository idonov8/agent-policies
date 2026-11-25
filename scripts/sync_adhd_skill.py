#!/usr/bin/env python3
"""Refresh the upstream i-have-adhd skill without installing plugins or hooks."""
import io
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid


SOURCE = 'https://codeload.github.com/ayghri/i-have-adhd/tar.gz/refs/heads/main'
FILES = ('SKILL.md', 'agents/openai.yaml', 'agents/gemini.toml')
LABEL = 'com.idonov.i-have-adhd-update'


def refresh(home):
    root = home / '.local/share/i-have-adhd'
    current = root / 'current'
    payload = subprocess.check_output([
        'curl', '--fail', '--silent', '--show-error', '--max-time', '30', SOURCE,
    ])
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        files = {}
        for name in FILES:
            member = archive.getmember(f'i-have-adhd-main/skills/i-have-adhd/{name}')
            if not member.isfile() or not 0 < member.size <= 256 * 1024:
                raise ValueError(f'Invalid upstream file: {name}')
            files[name] = archive.extractfile(member).read()
    if b'name: i-have-adhd' not in files['SKILL.md'].splitlines():
        raise ValueError('Unexpected upstream skill name')
    if all((current / name).is_file() and (current / name).read_bytes() == data
           for name, data in files.items()):
        return current

    versions = root / 'versions'
    versions.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(dir=root) as temp:
        staging = Path(temp)
        snapshot = staging / 'skill'
        (snapshot / 'agents').mkdir(parents=True)
        for name, data in files.items():
            (snapshot / name).write_bytes(data)
        version = versions / uuid.uuid4().hex
        snapshot.rename(version)
        link = staging / 'current'
        link.symlink_to(version.relative_to(root), target_is_directory=True)
        os.replace(link, current)
    return current


def install_schedule(home):
    root = home / '.local/share/i-have-adhd'
    # Keep the job independent of the checkout used to run the installer.
    updater = root / 'sync_adhd_skill.py'
    with tempfile.TemporaryDirectory(dir=root) as temp:
        staged = Path(temp) / updater.name
        shutil.copyfile(__file__, staged)
        os.replace(staged, updater)
    launch_agents = home / 'Library/LaunchAgents'
    launch_agents.mkdir(parents=True, exist_ok=True)
    plist = launch_agents / f'{LABEL}.plist'
    config = plistlib.dumps({
        'Label': LABEL,
        'ProgramArguments': [sys.executable, str(updater)],
        'RunAtLoad': True,
        'StartCalendarInterval': {'Hour': 12, 'Minute': 15},
        'StandardErrorPath': str(root / 'update.log'),
    })
    domain = f'gui/{os.getuid()}'
    service = f'{domain}/{LABEL}'
    loaded = subprocess.run(['launchctl', 'print', service], capture_output=True).returncode == 0
    if loaded and plist.is_file() and plist.read_bytes() == config:
        return
    if loaded:
        subprocess.run(['launchctl', 'bootout', service], check=True)
    if not plist.is_file() or plist.read_bytes() != config:
        plist.write_bytes(config)
    subprocess.run(['launchctl', 'bootstrap', domain, str(plist)], check=True)


if __name__ == '__main__':
    refresh(Path.home())
