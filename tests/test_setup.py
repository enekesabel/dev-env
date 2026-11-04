"""Run setup only in disposable homes, with external commands replaced by local fixtures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
STUB = r'''#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
home = pathlib.Path(os.environ['HOME'])
args = sys.argv[1:]
command = pathlib.Path(sys.argv[0]).name
with (home / 'commands.jsonl').open('a') as log:
    log.write(json.dumps([command, *args]) + '\n')
if command == 'git':
    pass
elif command == 'curl':
    pathlib.Path(args[args.index('-o') + 1]).write_text('# Shared instructions\n')
elif command == 'npx':
    action = args[args.index('skills') + 1]
    lockfile = pathlib.Path(os.environ['XDG_STATE_HOME']) / 'skills/.skill-lock.json'
    lock = json.loads(lockfile.read_text()) if lockfile.exists() else {'version': 3, 'skills': {}}
    if action == 'remove':
        for name in args[args.index('remove') + 1:args.index('-g')]:
            shutil.rmtree(home / '.agents/skills' / name)
            lock['skills'].pop(name, None)
    else:
        source = args[args.index('add') + 1]
        if source == os.environ.get('FAIL_SOURCE'):
            sys.exit(1)
        fixture = pathlib.Path(json.loads(os.environ['SOURCES'])[source])
        names = args[args.index('--skill') + 1:args.index('-a')]
        names = [n for n in names if n not in ('-g',)]
        if '*' in names:
            names = [p.name for p in fixture.iterdir()]
        root = home if '-g' in args else pathlib.Path.cwd()
        for name in names:
            dest = root / '.agents/skills' / name
            if dest.is_symlink():
                dest.unlink()
            elif dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(fixture / name, dest, symlinks=True)
            if '-g' in args:
                lock['skills'][name] = {'source': source}
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    lockfile.write_text(json.dumps(lock))
elif command in ('claude', 'codex'):
    statefile = home / (command + '-installed.json')
    state = json.loads(statefile.read_text()) if statefile.exists() else []
    if args[:2] == ['plugin', 'list']:
        print(json.dumps([{'id': name} for name in state]))
    elif args[:2] in (['plugin', 'install'], ['plugin', 'add']):
        if args[2] not in state:
            state.append(args[2])
    elif args[:2] in (['plugin', 'uninstall'], ['plugin', 'remove']):
        if os.environ.get('FAIL_UNINSTALL') == command:
            sys.exit(1)
        if args[2] in state:
            state.remove(args[2])
    statefile.write_text(json.dumps(state))
'''


class SetupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dev-env-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        stub = self.bin / 'stub'
        stub.write_text(STUB)
        stub.chmod(0o755)
        for name in ('git', 'curl', 'npx', 'claude', 'codex', 'cursor'):
            (self.bin / name).symlink_to(stub)
        for name in ('python3', 'node', 'jq'):
            (self.bin / name).symlink_to(shutil.which(name))
        self.sources = {}
        for source, names in {
            'enekesabel/dev-env': ('pr', 'code-review', 'mine'),
            'mattpocock/skills': ('tdd', 'pr', 'code-review'),
            'other/skills': ('handoff',),
        }.items():
            folder = self.root / source
            for name in names:
                skill = folder / name
                skill.mkdir(parents=True)
                # No final newline, a body name field, and a symlink catch accidental prose edits.
                (skill / 'SKILL.md').write_text(
                    f'---\nname: {name}\ndescription: Test\n---\nUse /tdd.\nname: body stays')
                (skill / 'support.txt').write_text('support')
                (skill / 'link.txt').symlink_to('support.txt')
            self.sources[source] = str(folder)
        self.list = self.root / 'skills.txt'
        self.env = {**os.environ, 'HOME': str(self.home),
                    'PATH': str(self.bin) + ':/usr/bin:/bin',
                    'CLAUDE_CONFIG_DIR': str(self.home / 'claude-config'),
                    'CODEX_HOME': str(self.home / 'codex-config'),
                    'XDG_CONFIG_HOME': str(self.home / '.config'),
                    'XDG_STATE_HOME': str(self.home / '.state'),
                    'NPM_CONFIG_CACHE': str(self.home / '.npm'),
                    'DEV_ENV_SKILLS_FILE': str(self.list), 'SOURCES': json.dumps(self.sources)}
        self.plugins = self.home / '.agents/skill-plugins'

    def run_setup(self, text, mode='refresh', success=True, **env):
        self.list.write_text(text)
        result = subprocess.run(['bash', str(REPO / 'setup.sh'), *([mode] if mode else [])],
                                cwd=self.root, env={**self.env, **env}, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode == 0, success, result.stdout)
        return result.stdout

    def commands(self):
        return [json.loads(line) for line in (self.home / 'commands.jsonl').read_text().splitlines()]

    def test_install_update_and_remove(self):
        initial = 'enekesabel/dev-env *\nmatt=mattpocock/skills tdd pr code-review\nmatt=other/skills handoff\n'
        self.run_setup(initial, mode='')
        self.assertTrue((self.home / '.agents/skills/mine/SKILL.md').exists())
        self.assertFalse((self.home / '.agents/skills/tdd').exists())
        plugin = self.plugins / 'plugins/matt'
        upstream = Path(self.sources['mattpocock/skills']) / 'tdd/SKILL.md'
        self.assertEqual((plugin / 'skills/tdd/SKILL.md').read_bytes(), upstream.read_bytes())
        self.assertTrue((plugin / 'skills/handoff/SKILL.md').exists())
        self.assertEqual(json.loads((plugin / '.claude-plugin/plugin.json').read_text())['name'], 'matt')
        self.assertEqual(json.loads((self.plugins / '.claude-plugin/marketplace.json').read_text())['plugins'],
                         [{'name': 'matt', 'source': './plugins/matt'}])
        cursor = self.home / '.cursor/plugins/local/matt/skills'
        self.assertEqual((cursor / 'matt:tdd/SKILL.md').read_bytes(),
                         upstream.read_bytes().replace(b'name: tdd', b'name: matt:tdd', 1))
        self.assertFalse((cursor / 'tdd').exists())
        self.assertFalse(any(p.is_symlink() for p in plugin.rglob('*')))
        self.assertFalse(any(p.is_symlink() for p in cursor.rglob('*')))
        upstream.write_text(upstream.read_text().replace('Test', 'Updated'))
        self.run_setup('enekesabel/dev-env *\nmatt=mattpocock/skills tdd\n')
        self.assertFalse((plugin / 'skills/pr').exists())
        self.assertFalse((cursor / 'matt:pr').exists())
        self.assertIn('Updated', (plugin / 'skills/tdd/SKILL.md').read_text())
        calls = self.commands()
        self.assertEqual(calls.count(['claude', 'plugin', 'install', 'matt@dev-env-skills']), 1)
        self.assertEqual(calls.count(['codex', 'plugin', 'add', 'matt@dev-env-skills']), 2)
        # Unrelated folders/plugins survive removing every managed prefix.
        (self.plugins / 'plugins/unmanaged').mkdir()
        (cursor.parent.parent / 'unmanaged').mkdir()
        self.run_setup('enekesabel/dev-env *\n')
        self.assertFalse(plugin.exists())
        self.assertFalse(cursor.parent.exists())
        self.assertTrue((self.plugins / 'plugins/unmanaged').exists())
        self.assertTrue((cursor.parent.parent / 'unmanaged').exists())
        for harness in ('claude', 'codex'):
            installed = json.loads((self.home / f'{harness}-installed.json').read_text())
            self.assertNotIn('matt@dev-env-skills', installed)

    def test_conflicts_and_invalid_prefix(self):
        for text in ('matt=mattpocock/skills tdd\nmattpocock/skills tdd\n',
                     'mattpocock/skills *\nmatt=mattpocock/skills tdd\n',
                     'matt=mattpocock/skills *\nmattpocock/skills tdd\n'):
            self.assertIn('both scoped and unscoped', self.run_setup(text, success=False))
        self.assertIn('invalid skill prefix', self.run_setup('../bad=other/skills handoff\n', success=False))
        self.assertFalse((self.home / 'commands.jsonl').exists())

    def test_migration_protects_wrappers_and_runs_once(self):
        shared = self.home / '.agents/skills'
        for name in ('tdd', 'code-review', 'pr'):
            (shared / name).mkdir(parents=True)
        lock = self.home / '.state/skills/.skill-lock.json'
        lock.parent.mkdir(parents=True)
        lock.write_text(json.dumps({'version': 3, 'skills': {
            'tdd': {'source': 'mattpocock/skills'},
            'code-review': {'source': 'mattpocock/skills'},
            'pr': {'source': 'enekesabel/dev-env'}}}))
        self.run_setup('enekesabel/dev-env *\nmatt=mattpocock/skills tdd\n')
        removals = [c for c in self.commands() if c[:4] == ['npx', '-y', 'skills', 'remove']]
        self.assertEqual(removals, [['npx', '-y', 'skills', 'remove', 'code-review', 'tdd', '-g', '-y']])
        self.assertTrue((shared / 'pr/SKILL.md').exists())
        self.assertTrue((shared / 'code-review/SKILL.md').exists())
        self.run_setup('enekesabel/dev-env *\n')
        self.assertEqual([c for c in self.commands() if 'remove' in c and c[0] == 'npx'], removals)

    def test_failed_build_preserves_published_plugin(self):
        self.run_setup('matt=mattpocock/skills tdd\n')
        self.run_setup('matt=other/skills handoff\n', success=False, FAIL_SOURCE='other/skills')
        self.assertTrue((self.plugins / 'plugins/matt/skills/tdd/SKILL.md').exists())

    def test_failed_uninstall_is_retried(self):
        self.run_setup('matt=mattpocock/skills tdd\n')
        self.assertIn('uninstall', self.run_setup('# empty\n', FAIL_UNINSTALL='codex'))
        self.assertEqual((self.plugins / 'codex-prefixes').read_text(), 'matt\n')
        self.run_setup('# empty\n')
        self.assertEqual((self.plugins / 'codex-prefixes').read_text(), '')

    def test_absent_harness_catches_up_without_removing_other_prefix(self):
        self.run_setup('matt=mattpocock/skills tdd\nother=other/skills handoff\n')
        (self.bin / 'codex').unlink()
        self.run_setup('other=other/skills handoff\n')
        self.assertEqual((self.plugins / 'codex-prefixes').read_text(), 'matt\nother\n')
        self.assertTrue((self.plugins / 'plugins/other/skills/handoff/SKILL.md').exists())
        (self.bin / 'codex').symlink_to(self.bin / 'stub')
        self.run_setup('other=other/skills handoff\n')
        self.assertEqual((self.plugins / 'codex-prefixes').read_text(), 'other\n')

    def test_untracked_wrappers_are_preserved_during_migration(self):
        for name in ('pr', 'code-review'):
            (self.home / '.agents/skills' / name).mkdir(parents=True)
        self.run_setup('matt=mattpocock/skills tdd\n')
        self.assertFalse(any(c[:4] == ['npx', '-y', 'skills', 'remove'] for c in self.commands()))


if __name__ == '__main__':
    unittest.main()
