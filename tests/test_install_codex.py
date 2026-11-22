"""Installer regression tests using disposable homes and package copies only.

Run: python -m unittest discover -s tests -p 'test_install_codex.py' -v
No personal skill directory, network, narration runtime, or Git command is used.
"""

import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PAYLOAD = {
    'SKILL.md', 'TRANSFER.md', 'agents/openai.yaml',
    'scripts/install_codex.py', 'scripts/setup_local_narration.py',
    'scripts/render_local_narration.py', 'scripts/serve_local.py',
    'references/budget-and-media.md', 'references/dependencies.md',
    'references/editorial.md', 'references/experience-and-chat.md',
    'references/first-run.md', 'references/local-narration.md',
    'references/quality-loop.md', 'references/setup-verification.md',
    'references/visual-design.md',
}


def snapshot(root):
    result = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ('link', os.readlink(path))
        elif path.is_file():
            result[relative] = ('file', hashlib.sha256(path.read_bytes()).hexdigest(),
                                path.stat().st_mtime_ns)
        elif path.is_dir():
            result[relative] = ('directory', path.stat().st_mtime_ns)
    return result


class InstallCodexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = Path(__file__).resolve().parents[1]
        helper = cls.repository / 'scripts/install_codex.py'
        spec = importlib.util.spec_from_file_location('install_codex', helper)
        cls.installer = importlib.util.module_from_spec(spec)
        old_bytecode = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(cls.installer)
        finally:
            sys.dont_write_bytecode = old_bytecode

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='article-installer-test-')
        self.addCleanup(temporary.cleanup)
        # Resolve platform aliases such as macOS /var -> /private/var. The
        # production installer deliberately rejects symlink path components.
        self.base = Path(temporary.name).resolve()
        self.home = self.base / 'Home with spaces'
        self.home.mkdir()
        self.source = self.base / 'Source package with spaces'
        for relative in PAYLOAD:
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.repository / relative, target)
        for relative in ['.env', '.git/config', '.venv/fixture.txt', 'media/private.txt',
                         'tests/not-payload.py', 'README.md']:
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('local-only test fixture\n', encoding='utf-8')
        self.skills = self.base / 'Custom host with spaces' / 'skills'
        self.target = self.skills / 'article-explainer'

    def install(self, **kwargs):
        return self.installer.install_skill(self.source, self.skills, **kwargs)

    def default(self, codex_home=None):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(Path, 'home', return_value=self.home):
            if codex_home is not None:
                os.environ['CODEX_HOME'] = str(codex_home)
            return self.installer.default_skills_dir()

    def cli(self, *arguments, codex_home=None):
        environment = {'HOME': str(self.home), 'USERPROFILE': str(self.home),
                       'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'}
        for name in ['SYSTEMROOT', 'WINDIR']:
            if name in os.environ:
                environment[name] = os.environ[name]
        if codex_home is not None:
            environment['CODEX_HOME'] = str(codex_home)
        return subprocess.run([sys.executable, '-I', '-B', str(self.source / 'scripts/install_codex.py'),
                               *arguments], cwd=self.home, env=environment, capture_output=True,
                              text=True, timeout=30)

    def symlink(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest('Symlink fixture unavailable: ' + str(error))

    def test_default_new_home_and_empty_codex_home(self):
        expected = self.home / '.agents/skills'
        self.assertEqual(Path(self.default()), expected)
        self.assertEqual(Path(self.default('')), expected)
        # Ordinary host configuration directories alone are not installations.
        (self.home / '.codex').mkdir()
        (self.home / '.agents').mkdir()
        self.assertEqual(Path(self.default()), expected)

    def test_default_sole_existing_install_and_ambiguity(self):
        codex = self.home / '.codex/skills/article-explainer'
        codex.mkdir(parents=True)
        self.assertEqual(Path(self.default()), codex.parent)
        agents = self.home / '.agents/skills/article-explainer'
        agents.mkdir(parents=True)
        with self.assertRaises(self.installer.InstallError):
            self.default()
        shutil.rmtree(codex)
        self.assertEqual(Path(self.default()), agents.parent)

    def test_codex_home_precedes_ambiguous_installs(self):
        for host in ['.codex', '.agents']:
            (self.home / host / 'skills/article-explainer').mkdir(parents=True)
        custom = self.home / 'Explicit host'
        self.assertEqual(Path(self.default(custom)), custom / 'skills')
        self.assertFalse(custom.exists())

    def test_real_cli_dry_run_from_other_cwd_writes_nothing(self):
        custom = self.home / 'Explicit missing host'
        before = snapshot(self.base)
        result = self.cli('--dry-run', codex_home=custom)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.base), before)
        self.assertIn(str(custom / 'skills/article-explainer'), result.stdout)
        self.assertIn(str(self.source), result.stdout)

    def test_real_cli_codex_home_and_explicit_directory_precedence(self):
        custom = self.home / 'Explicit host'
        result = self.cli(codex_home=custom)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = custom / 'skills/article-explainer'
        self.assertTrue((installed / 'SKILL.md').is_file())
        result = self.cli('--skills-dir', str(self.skills), codex_home=custom)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / 'SKILL.md').is_file())

    def test_only_exact_payload_bytes_are_installed(self):
        self.install()
        files = {path.relative_to(self.target).as_posix() for path in self.target.rglob('*') if path.is_file()}
        self.assertEqual(len(files), 16)
        self.assertEqual(files, PAYLOAD)
        for relative in PAYLOAD:
            self.assertEqual((self.target / relative).read_bytes(), (self.source / relative).read_bytes())

    def test_identical_install_is_noop_even_with_update(self):
        self.install()
        before = snapshot(self.base)
        self.install()
        self.install(update=True)
        self.assertEqual(snapshot(self.base), before)

    def test_change_refused_without_update_and_dry_run_preserves_it(self):
        self.install()
        (self.target / 'SKILL.md').write_text((self.target / 'SKILL.md').read_text() + '\nLocal edit.\n')
        (self.target / 'local-edit.txt').write_text('keep me')
        before = snapshot(self.base)
        with self.assertRaises(self.installer.InstallError):
            self.install()
        self.assertEqual(snapshot(self.base), before)
        self.install(update=True, dry_run=True)
        self.assertEqual(snapshot(self.base), before)

    def test_update_preserves_entire_old_tree_outside_discovery(self):
        self.install()
        (self.target / 'SKILL.md').write_text((self.target / 'SKILL.md').read_text() + '\nLocal edit.\n')
        (self.target / 'local-edit.txt').write_text('keep me')
        old = snapshot(self.target)
        self.install(update=True)
        extras = list(self.base.rglob('local-edit.txt'))
        self.assertEqual(len(extras), 1)
        backup = extras[0].parent
        self.assertFalse(backup.is_relative_to(self.skills))
        self.assertEqual(snapshot(backup), old)
        self.assertFalse((self.target / 'local-edit.txt').exists())
        self.assertEqual((self.target / 'SKILL.md').read_bytes(), (self.source / 'SKILL.md').read_bytes())

    @unittest.skipIf(os.name == 'nt', 'POSIX mode privacy check; Windows requires its own ACL policy')
    def test_backup_keeps_parent_directory_privacy(self):
        self.install()
        # A legacy copy may depend on its enclosing skills directory for privacy.
        self.skills.parent.chmod(0o755)
        self.skills.chmod(0o700)
        self.target.chmod(0o755)
        (self.target / 'local-edit.txt').write_text('private local fixture')
        self.install(update=True)
        backup = next(self.base.rglob('local-edit.txt')).parent
        self.assertEqual(stat.S_IMODE(backup.parent.stat().st_mode) & 0o077, 0)

    @unittest.skipIf(os.name == 'nt', 'POSIX mode privacy check; Windows requires its own ACL policy')
    def test_permissive_existing_backup_root_is_refused_before_changes(self):
        self.install()
        (self.target / 'local-edit.txt').write_text('preserve old installation')
        backup_root = self.skills.parent / 'article-explainer-backups'
        backup_root.mkdir()
        backup_root.chmod(0o755)
        before = snapshot(self.base)
        for dry_run in [True, False]:
            with self.assertRaises(self.installer.InstallError):
                self.install(update=True, dry_run=dry_run)
            self.assertEqual(snapshot(self.base), before)

    def test_update_swap_failure_restores_previous_install(self):
        self.install()
        (self.target / 'local-edit.txt').write_text('preserve on failure')
        old = snapshot(self.target)
        replace = os.replace
        failed = False
        def fail_first_publication(source, destination):
            nonlocal failed
            if Path(destination) == self.target and not failed:
                failed = True
                raise OSError('simulated publication failure')
            return replace(source, destination)
        with mock.patch.object(self.installer.os, 'replace', side_effect=fail_first_publication):
            with self.assertRaises(OSError):
                self.install(update=True)
        self.assertTrue(failed)
        self.assertEqual(snapshot(self.target), old)

    def test_missing_payload_does_not_create_destination(self):
        (self.source / 'references/editorial.md').unlink()
        with self.assertRaises(self.installer.InstallError):
            self.install()
        self.assertFalse(self.skills.exists())

    def test_failed_rollback_keeps_backup_and_reports_recovery_path(self):
        self.install()
        (self.target / 'local-edit.txt').write_text('preserve even if restore fails')
        old = snapshot(self.target)
        replace = os.replace
        def reject_target_writes(source, destination):
            if Path(destination) == self.target:
                raise OSError('simulated publication and rollback failure')
            return replace(source, destination)
        with mock.patch.object(self.installer.os, 'replace', side_effect=reject_target_writes):
            with self.assertRaises(self.installer.InstallError) as caught:
                self.install(update=True)
        backups = list(self.base.rglob('local-edit.txt'))
        self.assertEqual(len(backups), 1)
        backup = backups[0].parent
        self.assertFalse(backup.is_relative_to(self.skills))
        self.assertEqual(snapshot(backup), old)
        self.assertIn(str(backup), str(caught.exception))
        self.assertIn(str(self.target), str(caught.exception))

    def test_source_file_symlink_rejected(self):
        target = self.source / 'references/editorial.md'
        target.unlink()
        self.symlink(target, self.source / 'references/quality-loop.md')
        with self.assertRaises(self.installer.InstallError):
            self.install()
        self.assertFalse(self.skills.exists())

    def test_destination_ancestor_symlink_rejected(self):
        outside = self.base / 'Outside destination'
        outside.mkdir()
        self.symlink(self.skills.parent, outside, directory=True)
        with self.assertRaises(self.installer.InstallError):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_target_or_nested_symlink_rejected(self):
        self.install()
        outside = self.base / 'outside.txt'
        outside.write_text('untouched')
        self.symlink(self.target / 'unexpected-link.txt', outside)
        with self.assertRaises(self.installer.InstallError):
            self.install(update=True)
        self.assertEqual(outside.read_text(), 'untouched')
        self.assertTrue((self.target / 'unexpected-link.txt').is_symlink())

    def test_source_destination_overlap_rejected(self):
        with self.assertRaises(self.installer.InstallError):
            self.installer.install_skill(self.source, self.source / 'skills')
        self.assertFalse((self.source / 'skills').exists())


if __name__ == '__main__':
    unittest.main()
