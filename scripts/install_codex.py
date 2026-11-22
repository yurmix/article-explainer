#!/usr/bin/env python3
"""Install this skill into local Codex. Python 3.9+, standard library, no network.

Run from any folder: python /path/to/article-explainer/scripts/install_codex.py
Use --dry-run to inspect without writes; --update permits replacing a recognized
different installation after preserving its entire old folder in a backup.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import uuid


SKILL_NAME = "article-explainer"
PAYLOAD_FILES = (
    "SKILL.md", "TRANSFER.md", "agents/openai.yaml",
    "scripts/install_codex.py", "scripts/render_local_narration.py",
    "scripts/serve_local.py", "scripts/setup_local_narration.py",
    "references/budget-and-media.md", "references/dependencies.md",
    "references/editorial.md", "references/experience-and-chat.md",
    "references/first-run.md", "references/local-narration.md",
    "references/quality-loop.md", "references/setup-verification.md",
    "references/visual-design.md",
)


class InstallError(Exception):
    """An installation cannot proceed without risking an existing file."""


def normalized(path):
    path = Path(os.path.abspath(os.path.expanduser(str(path))))
    # macOS uses these fixed system aliases; do not resolve arbitrary user links.
    if sys.platform == "darwin" and len(path.parts) > 1 and path.parts[1] in ("var", "tmp"):
        alias = Path("/") / path.parts[1]
        target = Path("/private") / path.parts[1]
        if alias.is_symlink():
            link = Path(os.readlink(alias))
            link = link if link.is_absolute() else alias.parent / link
            if os.path.normpath(str(link)) == str(target):
                path = target.joinpath(*path.parts[2:])
    return path


def within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def safe_path(path):
    """Reject symlinks and Windows reparse points, including path ancestors."""
    path = normalized(path)
    for current in (*reversed(path.parents), path):
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        if stat.S_ISLNK(info.st_mode) or reparse:
            raise InstallError(f"Unsafe symlink or junction: {current}")
        if current != path and not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"A path ancestor is not a directory: {current}")
    return path


def default_skills_dir():
    """Honor explicit Codex configuration, otherwise reuse one existing install."""
    configured = os.environ.get("CODEX_HOME", "")
    if configured.strip():
        return normalized(Path(configured) / "skills")
    home = Path.home()
    candidates = [home / ".agents" / "skills", home / ".codex" / "skills"]
    existing = [parent for parent in candidates if os.path.lexists(parent / SKILL_NAME)]
    if len(existing) > 1:
        raise InstallError("Both ~/.agents/skills/article-explainer and ~/.codex/skills/article-explainer exist. Choose one with --skills-dir.")
    return normalized(existing[0] if existing else candidates[0])


def recognized(folder):
    marker = safe_path(folder / "SKILL.md")
    if not marker.is_file():
        return False
    lines = marker.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    found = False
    for line in lines[1:]:
        if line.strip() == "---":
            return found
        if re.fullmatch(r'''name:\s*(?:article-explainer|'article-explainer'|"article-explainer")\s*''', line):
            found = True
    return False


def build_payload(source_root):
    source_root = safe_path(source_root)
    if not source_root.is_dir() or not recognized(source_root):
        raise InstallError(f"Source is not an Article Explainer skill: {source_root}")
    payload = {}
    for relative in PAYLOAD_FILES:
        path = safe_path(source_root / relative)
        if not path.is_file() or not stat.S_ISREG(path.lstat().st_mode):
            raise InstallError(f"Required payload file is missing or not regular: {path}")
        payload[relative] = path.read_bytes()
    return payload


def tree_snapshot(folder):
    """Fingerprint files and empty directories while rejecting unsafe old trees."""
    folder = safe_path(folder)
    if not os.path.lexists(folder):
        return None
    if not folder.is_dir():
        raise InstallError(f"Installation path is not a directory: {folder}")
    entries = {}
    for current, directories, files in os.walk(folder, followlinks=False):
        for name in directories + files:
            path = safe_path(Path(current) / name)
            relative = path.relative_to(folder).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                entries[relative + "/"] = None
            elif stat.S_ISREG(mode):
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                entries[relative] = digest.hexdigest()
            else:
                raise InstallError(f"Unsupported file type in existing installation: {path}")
    return entries


def expected_snapshot(payload):
    entries = {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}
    for name in payload:
        for parent in Path(name).parents:
            if str(parent) != ".":
                entries[parent.as_posix() + "/"] = None
    return entries


def verify_backup_privacy(backup_root):
    """Do not move an old skill outside its private parent into a shared folder."""
    if not os.path.lexists(backup_root):
        return
    info = safe_path(backup_root).lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise InstallError(f"Backup path is not a directory: {backup_root}")
    # POSIX mode checks do not verify Windows ACLs; native Windows security
    # behavior is unverified and must not be described as enforced by chmod.
    if os.name == "posix":
        if info.st_uid != os.getuid():
            raise InstallError(f"Backup directory is not owned by the current user: {backup_root}. Choose a private --skills-dir location.")
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise InstallError(f"Backup directory permits group or other access: {backup_root}. Set this dedicated directory to owner-only permissions (0700), then retry. No existing permissions were changed.")


def backup_directory(skills_dir, source_root):
    backup_root = safe_path(skills_dir.parent / "article-explainer-backups")
    discovery_roots = [skills_dir, normalized(Path.home() / ".agents" / "skills"),
                       normalized(Path.home() / ".codex" / "skills")]
    if os.environ.get("CODEX_HOME", "").strip():
        discovery_roots.append(normalized(Path(os.environ["CODEX_HOME"]) / "skills"))
    if any(within(backup_root, root) for root in discovery_roots) or within(backup_root, source_root):
        raise InstallError("Backup would be inside a skill discovery or source folder. Choose a non-nested --skills-dir.")
    verify_backup_privacy(backup_root)
    return backup_root


def install_skill(source_root, skills_dir, *, update=False, dry_run=False):
    source_root = safe_path(source_root)
    skills_dir = safe_path(skills_dir)
    destination = safe_path(skills_dir / SKILL_NAME)
    if within(destination, source_root) or within(source_root, destination):
        raise InstallError("Source and destination overlap; install from a separate downloaded checkout.")
    payload = build_payload(source_root)
    if os.path.lexists(destination) and not recognized(destination):
        raise InstallError(f"Refusing an unrecognized existing folder: {destination}")
    previous = tree_snapshot(destination)
    expected = expected_snapshot(payload)
    result = {"source": str(source_root), "destination": str(destination), "files": list(PAYLOAD_FILES),
              "status": "unchanged" if previous == expected else "update" if previous is not None else "install",
              "dry_run": dry_run, "backup": None}
    if result["status"] == "unchanged":
        return result
    if previous is not None and not update:
        raise InstallError(f"A different installation exists at {destination}. Inspect it, then use --update to preserve it in a backup and install this version.")
    backup_root = backup_directory(skills_dir, source_root) if previous is not None else None
    if dry_run:
        if backup_root:
            result["backup_directory"] = str(backup_root)
        return result

    stage = None
    backup = None
    moved_old = False
    try:
        skills_dir.mkdir(parents=True, exist_ok=True)
        safe_path(skills_dir)
        stage = Path(tempfile.mkdtemp(prefix=".article-explainer-stage-", dir=str(skills_dir.parent)))
        for relative, data in payload.items():
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        if tree_snapshot(stage) != expected:
            raise InstallError("Staged payload verification failed; the existing skill was not changed.")
        if tree_snapshot(destination) != previous:
            raise InstallError("The destination changed during preparation; refusing to overwrite it.")
        if previous is not None:
            backup_root.mkdir(mode=0o700, parents=True, exist_ok=True)
            verify_backup_privacy(backup_root)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = backup_root / f"{SKILL_NAME}-{stamp}-{uuid.uuid4().hex}"
            os.replace(destination, backup)
            moved_old = True
        try:
            safe_path(destination)
            if os.path.lexists(destination):
                raise InstallError("A new destination appeared; refusing to replace it.")
            os.replace(stage, destination)
            stage = None
        except Exception as error:
            if moved_old:
                try:
                    safe_path(destination)
                    if os.path.lexists(destination):
                        raise InstallError("A new destination appeared during rollback.")
                    os.replace(backup, destination)
                    moved_old = False
                except Exception as rollback_error:
                    raise InstallError(f"Installation failed ({error}); automatic restore failed ({rollback_error}). Your old skill is preserved at {backup}. Move the current destination aside, then move this backup to {destination}.") from error
            raise
        result["backup"] = str(backup) if moved_old else None
        return result
    finally:
        if stage is not None and stage.is_dir():
            # Only remove our private staging folder, never the old installation.
            shutil.rmtree(stage)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, help="Parent skills folder; article-explainer is installed beneath it")
    parser.add_argument("--dry-run", action="store_true", help="Read-only validation and plan; create no folders or files")
    parser.add_argument("--update", action="store_true", help="Permit replacing a different recognized installation, retaining a complete backup")
    args = parser.parse_args(argv)
    try:
        source = normalized(Path(__file__).parent.parent)
        result = install_skill(source, args.skills_dir if args.skills_dir is not None else default_skills_dir(),
                               update=args.update, dry_run=args.dry_run)
    except (InstallError, OSError, UnicodeError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print(f"Source: {result['source']}")
    if result["status"] == "unchanged":
        print(f"Already identical; nothing changed: {result['destination']}")
    else:
        print(f"{'Would ' if args.dry_run else ''}{result['status'].capitalize()} {len(result['files'])} skill files: {result['destination']}")
        if result.get("backup_directory"):
            print(f"Existing skill would be preserved under: {result['backup_directory']}")
        if result["backup"]:
            print(f"Complete previous skill preserved at: {result['backup']}")
            print(f"To restore: move {result['destination']} aside, then move {result['backup']} to {result['destination']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
