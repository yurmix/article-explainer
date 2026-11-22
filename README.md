# Article Explainer

A portable agent skill for turning an article into a faithful narrated explainer website: animated scenes, a readable source, and source-grounded questions when a supported chat connection is available. It can also guide a standalone video export.

Use it in a shell-capable Codex or Claude Code session with your existing account. The local English narration route uses free software and runs on your computer after a one-time download. The package includes setup and playback helpers; model weights and Python environments are downloaded separately.

## Quality bar

Every run must meet four criteria:

- Compelling visuals that explain relationships and consequences.
- A pleasant, easy-to-follow voice, assessed through actual listening.
- Concise, source-faithful content that builds understanding.
- Self-contained first-time setup with justified installation and real verification.

The skill provides free-first and explicitly budgeted enhanced modes. Free-first starts with the existing agent seat and free local resources. It does not activate credits or configure a paid model API automatically. Embedded chat needs its own verified connection; authoring through a subscription does not establish that connection.

## Install into local Codex

The included [installer](scripts/install_codex.py) copies the skill into your personal Codex skills folder. It requires Python 3.9 or newer and uses only its standard library. Installation is offline after you obtain this repository; it does not download narration models, change Codex settings, request an API key, or incur a charge. Narration setup is a separate first-run step.

On macOS or Linux, open a terminal and run:

```sh
git clone https://github.com/yurmix/article-explainer.git
cd article-explainer
python3 scripts/install_codex.py --dry-run
python3 scripts/install_codex.py
```

On Windows, use PowerShell and the Python launcher:

```powershell
git clone https://github.com/yurmix/article-explainer.git
cd article-explainer
py -3 scripts/install_codex.py --dry-run
py -3 scripts/install_codex.py
```

If Git is unavailable, use GitHub's **Code → Download ZIP**, extract the archive, and open a terminal in the extracted folder; run just the Python commands. If Python is missing, either use the manual copy below or follow [Python setup](references/first-run.md#if-python-is-missing-or-incompatible). Python 3.12 also supports the separate narration helper. The installer is tested on macOS; native Windows/Linux execution remains unverified.

The dry run prints the source, destination, and proposed action without writing files. The installer copies only the packaged skill files and verifies their bytes. Repository history, tests, private configuration, logs, and generated media are excluded.

### Where it installs

For a new setup, the default is `~/.agents/skills/article-explainer/`, the personal location in the [official Codex skills guide](https://learn.chatgpt.com/docs/build-skills). To preserve an existing installation, it reuses a sole existing `article-explainer` in either `~/.agents/skills/` or `~/.codex/skills/`. If both exist, it asks you to choose a directory explicitly. An explicitly set `CODEX_HOME` selects its `skills/` directory, matching the bundled Codex installer convention. An explicit `--skills-dir` overrides these choices:

```sh
python3 scripts/install_codex.py --skills-dir "/path/to/codex/skills" --dry-run
python3 scripts/install_codex.py --skills-dir "/path/to/codex/skills"
```

Pass the parent skills directory; the script adds `article-explainer`. Choose a location your Codex installation actually loads. `~` means your user home directory, including on Windows. Run as your ordinary user; administrator access is unnecessary.

### Use it

It should be available on your next Codex turn. Type `$article-explainer` and give it an article, for example:

```text
$article-explainer https://example.com/article
Create a narrated animated website for a general audience. Use my existing
seat and free local tools, with no API credits or additional spending.
Work locally and verify all four quality criteria.
```

Codex detects skill changes automatically; restart Codex if the skill does not appear. Confirm that the printed destination is loaded by your host and that the skill is not disabled in your configuration. Do not create another copy to troubleshoot discovery.

### Update, restore, or remove

From your repository clone:

```sh
git pull --ff-only
python3 scripts/install_codex.py --update --dry-run
python3 scripts/install_codex.py --update
```

Use `py -3` in PowerShell. For a ZIP installation, extract the newer ZIP and run its installer with `--update`. Reuse `--skills-dir` if you selected a custom directory. Identical files produce a no-op. Different existing files require `--update`; the installer preserves the entire old skill, including local edits and extra files, in a backup outside the skills directory before replacing it. It prints the backup and restore destination. Local customizations remain in that backup rather than being merged automatically.

To restore, move the current installed `article-explainer` folder out of the skills directory, then move the printed backup folder into the printed restore destination. To uninstall, remove only the installed `article-explainer` folder. Keep any backup you still need. Neither action removes projects or narration environments.

### Manual copy or another host

Without Python, create `~/.agents/skills/article-explainer/` and copy `SKILL.md`, `TRANSFER.md`, `agents/`, `references/`, and `scripts/` from this repository into it. Preserve an already recognized `~/.codex/skills/` installation instead of creating a duplicate. Keep local edits before replacing existing files.

Claude Code uses `~/.claude/skills/article-explainer/`; the [transfer guide](TRANSFER.md) covers that route and adaptation tests. Restricted chat environments need a supported executor for installation, synthesis, and local playback. The [first-run guide](references/first-run.md) covers missing Python, narration setup, verification, and opening or reopening a finished site.

## Included tools

| Helper | Purpose |
| --- | --- |
| `scripts/install_codex.py` | Install or safely update the skill in a local Codex skills folder |
| `scripts/setup_local_narration.py` | Inspect, plan, and install an isolated CPU narration runtime |
| `scripts/render_local_narration.py` | Generate recorded English narration and timing data from scene scripts |
| `scripts/serve_local.py` | Serve a local static site with working audio seeking, using Python's standard library |

No Node.js or video encoder is needed for the basic website route. Additional tools are selected only when the requested output needs them. Allow at least 3 GiB free for narration setup; the measured Mac installation and Python bootstrap occupied about 1.8 GiB after installation.

## Verification and scope

An independent fresh-environment test passed on Apple Silicon macOS 26.6.2 with CPython 3.12.16. It covered missing-Python setup, fresh dependency/model downloads, offline speech generation, repeated setup, and browser seeking and reopening. See the [verification record](references/setup-verification.md) for exact versions and limits.

Windows x64 and Linux x64 instructions and package availability were reviewed; native execution on those platforms remains untested. Claude execution and a second physical laptop were not tested. Only American English narration has been validated. New output still requires visual, editorial, and listening review; technical audio checks do not establish pleasantness.

Read [SECURITY.md](SECURITY.md) before installing into an existing project or serving local files. Runtime dependencies and downloaded models retain their respective licenses; those assets are not part of this repository.

## Run the bundled tests

From the repository root, with Python 3.12 available:

```sh
python3.12 -B -m unittest discover -s tests -v
```

The tests use temporary installation fixtures and local HTTP requests. They install no dependencies and make no external network requests or audible playback. Platforms without symlink permission skip the symlink-specific cases.
