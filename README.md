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

## Get started

Clone or download this repository, keeping its contents together:

```sh
git clone https://github.com/yurmix/article-explainer.git
```

Open a writable project in your agent and ask it to read `article-explainer/SKILL.md`, then give it the article URL. For example:

> Use Article Explainer with this article. Create a narrated animated website for a general audience. Use my existing seat and free local tools, with no API credits or additional spending. Work locally and verify all four quality criteria.

For persistent discovery, place the complete folder at the location your host uses:

| Host | Typical personal skill location |
| --- | --- |
| Codex | `~/.agents/skills/article-explainer/` |
| Claude Code | `~/.claude/skills/article-explainer/` |

Preserve an existing recognized host configuration instead of installing duplicate copies. Restricted chat environments need a supported executor for installation, synthesis, and local playback.

Follow the [first-run guide](references/first-run.md) for missing Python, platform checks, dependency installation, narration verification, and opening or reopening a finished site. The [transfer guide](TRANSFER.md) includes a Claude adaptation prompt and behavioral tests.

## Included tools

| Helper | Purpose |
| --- | --- |
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

The server tests use temporary fixtures and loopback requests. They install no dependencies and make no external network requests or audible playback. Platforms without symlink permission skip the symlink-specific cases.
