# First run on another laptop

A successful transfer means a new user can get from the skill ZIP to a playable, narrated result without borrowing the original author's environment. Perform setup for the user where tools allow; do not merely hand them a dependency list. Reuse already authorized free installation work. Host permission dialogs and organizational restrictions still apply.

## Unpack and load the whole skill

Extract `article-explainer.zip` using the operating system's archive tool. Keep the complete folder together. Open an ordinary writable project folder in a shell-capable Codex or Claude Code session, signed in through the user's existing seat. Ask the host to read the extracted `article-explainer/SKILL.md`; this avoids requiring a package manager just to start.

For persistent discovery, copy the complete folder to one host location, preserving `article-explainer/SKILL.md` one level below `skills`:

| Host | Personal location | Project location |
| --- | --- | --- |
| Codex | `~/.agents/skills/article-explainer/` | `.agents/skills/article-explainer/` |
| Claude Code | `~/.claude/skills/article-explainer/` | `.claude/skills/article-explainer/` |

On Windows, `~` means the signed-in user's home directory. Use the host's configured location if it differs; avoid installing duplicate copies. Confirm the host can find the skill, then invoke it by name with the article URL. These paths come from the current [Codex skills guide](https://learn.chatgpt.com/docs/build-skills) and [Claude Code skills guide](https://code.claude.com/docs/en/skills). A terminal skill folder is not automatically available to Claude web/Cowork sessions; use that surface's supported skill-upload route and verify its actual tools.

A restricted chat can read the workflow, adapt the source, and produce files only to the extent its tools permit. It cannot install laptop software or keep a local server running without a supported executor. Explain that boundary and guide a shell-capable session; do not claim a runnable local result from instructions alone.

## Check first; choose the smallest route

Inspect OS, CPU architecture, Python executable/version, writable disk space, browser/preview access, and permission to download public packages. Do not assume Homebrew, uv, Node, FFmpeg, Sites, HeyGen, or an audio-listening tool exists.

| Requested work | Minimal route |
| --- | --- |
| Article analysis and website authoring | Existing agent seat and local files |
| Replay a finished static website | Browser, Python, and the bundled local server; no narration model needed |
| Generate fresh English neural narration | Bundled setup helper, a compatible Python, verified model assets, local CPU |
| Standalone video export | Add a renderer/encoder only when that export is selected |
| Embedded chat | Separately verified host-native/subscription or local-model connection |

When a compatible Python already works, skip Python installation. The current narration route targets CPython 3.12; run the helper's `plan` before downloading its stack. Apple Silicon execution was tested on macOS 26.6.2; macOS 14 is the dependency wheels' compatibility floor, not another tested OS version. Windows x64 and Linux x64 with glibc 2.28+ have verified CPU-wheel availability but have not been executed here; their local smoke test must pass. Other targets need a compatible adapted route, as reported by `plan`. Do not treat the newest Python version as automatically compatible with pinned neural packages.

For a strict seat-only run: no model API calls, promotional API credits, keys, credit activation, top-ups, or paid resets. Public software/model downloads are not inference API usage. At normal seat exhaustion, preserve progress and wait for the ordinary allowance to return. An unavailable embedded-chat route must not block independent media production; label it unavailable and offer questions in the existing source-aware host chat.

## If Python is missing or incompatible

The agent should choose **one** route, explain the required setup, and complete it within the user's authorization. Do not install several managers.

- **macOS:** Python.org provides signed installers; follow its [macOS instructions](https://docs.python.org/3/using/mac.html). Run the bundled `Install Certificates.command` if HTTPS verification fails. Select a compatible available release, not a security-only release page with no installer. Leave Apple's system Python alone.
- **Windows:** the official [Python install manager](https://docs.python.org/3/using/windows.html) can be installed from Python.org or Microsoft Store. Then `py install 3.12` installs the requested runtime, and `py -3.12 --version` verifies it. If an old launcher owns `py`, use the install manager's `pymanager install 3.12`, then select the verified interpreter.
- **Linux:** use the distribution's official Python package if compatible. For Ubuntu, `sudo apt install python3-full` includes the standard library and virtual-environment support; confirm the resulting version before the narration setup. Follow [Ubuntu's guide](https://documentation.ubuntu.com/ubuntu-for-developers/howto/python-setup/). Other distributions require their own package names; do not replace their system Python.

When those routes do not offer the required version conveniently, **uv is an optional bootstrap**, not a prerequisite assumed by the skill. Its standalone installer requires no existing Python. The following private setup stays in the current working folder and leaves shell profiles alone, using the official [installer options](https://docs.astral.sh/uv/reference/installer/) and [storage variables](https://docs.astral.sh/uv/reference/environment/). Download and read the installer before executing it.

macOS/Linux, in a writable project folder with `curl`:

```sh
bootstrap_dir="$PWD/.article-explainer-bootstrap"
mkdir -p "$bootstrap_dir"
curl -LsSf https://astral.sh/uv/install.sh -o "$bootstrap_dir/install-uv.sh"
cat "$bootstrap_dir/install-uv.sh"
# After inspecting the installer:
export UV_INSTALL_DIR="$bootstrap_dir/uv"
export UV_UNMANAGED_INSTALL="$bootstrap_dir/uv"
export UV_NO_MODIFY_PATH=1
export UV_PYTHON_INSTALL_DIR="$bootstrap_dir/python"
export UV_PYTHON_BIN_DIR="$bootstrap_dir/python-bin"
export UV_PYTHON_CACHE_DIR="$bootstrap_dir/python-archives"
export UV_CACHE_DIR="$bootstrap_dir/cache"
export UV_NO_CONFIG=1
sh "$bootstrap_dir/install-uv.sh"
"$bootstrap_dir/uv/uv" --version
"$bootstrap_dir/uv/uv" python install 3.12
"$bootstrap_dir/uv/uv" python find --managed-python --no-project --system 3.12
```

For Windows PowerShell:

```powershell
$bootstrapDir = Join-Path (Get-Location) ".article-explainer-bootstrap"
New-Item -ItemType Directory -Force $bootstrapDir | Out-Null
Invoke-WebRequest https://astral.sh/uv/install.ps1 -OutFile "$bootstrapDir\install-uv.ps1"
Get-Content "$bootstrapDir\install-uv.ps1"
# After inspecting the installer, if current host policy permits it:
$env:UV_INSTALL_DIR = "$bootstrapDir\uv"
$env:UV_UNMANAGED_INSTALL = "$bootstrapDir\uv"
$env:UV_NO_MODIFY_PATH = "1"
$env:UV_PYTHON_INSTALL_DIR = "$bootstrapDir\python"
$env:UV_PYTHON_BIN_DIR = "$bootstrapDir\python-bin"
$env:UV_PYTHON_CACHE_DIR = "$bootstrapDir\python-archives"
$env:UV_CACHE_DIR = "$bootstrapDir\cache"
$env:UV_NO_CONFIG = "1"
$env:UV_PYTHON_NO_REGISTRY = "1"
powershell -NoProfile -File "$bootstrapDir\install-uv.ps1"
& "$bootstrapDir\uv\uv.exe" --version
& "$bootstrapDir\uv\uv.exe" python install 3.12
& "$bootstrapDir\uv\uv.exe" python find --managed-python --no-project --system 3.12
```

If policy blocks the script, use Astral's [official prebuilt release ZIP](https://github.com/astral-sh/uv/releases), or the Python install manager. Do not silently weaken a global execution policy. If `curl` is absent on Linux, replace its download line with `wget -qO "$bootstrap_dir/install-uv.sh" https://astral.sh/uv/install.sh`. If neither downloader exists, use the browser to get the matching OS/architecture archive from the official releases page, extract its `uv` executable into the chosen `uv` folder, and resume at the version check. These alternatives follow the [official uv installation page](https://docs.astral.sh/uv/getting-started/installation/).

Save the final command's printed interpreter path and verify `--version` with that exact executable. The flags exclude ambient project virtual environments; plain `uv python find` can unexpectedly select one in a parent folder. Use the recorded path directly for subsequent commands, including after a terminal restart. These commands follow [uv's Python management guide](https://docs.astral.sh/uv/guides/install-python/) and [command reference](https://docs.astral.sh/uv/reference/cli/#uv-python-find). uv-managed Python comes from Astral's Python standalone builds, not Python.org installers. Keep this bootstrap folder where installed; moving/deleting it breaks environments that depend on its Python. uv itself is not required during rendering or playback.

## Prepare and prove local narration

Run from the extracted skill folder. Choose a project directory outside the skill package. Replace the interpreter with its verified absolute path when necessary, and quote paths with spaces.

macOS/Linux, with `python3.12` available:

```sh
python3.12 scripts/setup_local_narration.py check --project-dir "../My Explainer"
python3.12 scripts/setup_local_narration.py plan --project-dir "../My Explainer"
python3.12 scripts/setup_local_narration.py install --project-dir "../My Explainer"
```

Windows PowerShell, with the official launcher/runtime available:

```powershell
py -3.12 .\scripts\setup_local_narration.py check --project-dir "..\My Explainer"
py -3.12 .\scripts\setup_local_narration.py plan --project-dir "..\My Explainer"
py -3.12 .\scripts\setup_local_narration.py install --project-dir "..\My Explainer"
```

For a returned interpreter path containing spaces, use `"/full/path/python3.12" ...` in a POSIX shell or `& "C:\full path\python.exe" ...` in PowerShell. No virtual-environment activation or PowerShell policy change is needed for the helper.

`check` and `plan` must remain local and read-only. Inspect the plan's Python/platform result, download sources, state location, and space estimate before `install`. The installer owns only the selected project's `.article-explainer/narration/` environment, models, cache, smoke output, and provenance. Allow at least the plan's conservative free-space estimate; dependency downloads can be much larger than the model alone. It must verify/reuse successful assets on repetition rather than rebuild the environment every run.

Inspection must not execute the project's Python or import its packages. Reusing an existing nonempty runtime is an execution decision: add `--trust-existing-runtime` to `install` only for an environment you created and trust. For example, rerun your own verified project with `python3.12 scripts/setup_local_narration.py install --project-dir "../My Explainer" --trust-existing-runtime`. An ownership marker or package metadata does not establish trust. For an inherited or unknown environment, choose a fresh project directory. An agent can retain this flag for its own previously verified setup within the user's authorization; it need not ask for repetitive conversational confirmation.

A successful install must run the bundled renderer on the bundled smoke input. Within `.article-explainer/narration/`, inspect `smoke/media/narration.wav`, `smoke/verification.json`, and `provenance.json`; the helper also prints the working isolated interpreter and ready state. Verify durations and hashes, then play the sample. A successful import or installer exit is not the smoke test. Naturalness requires actual listening; ask the user if the host cannot hear. Only then synthesize the article with the accepted voice, following [local-narration.md](local-narration.md).

If setup fails, preserve the complete diagnostic, identify its stage, and fix that cause before repeating. Missing `venv` means install the distribution's matching component; certificate failures call for the platform's certificate repair, not disabled TLS; an unavailable wheel calls for a compatible supported interpreter/platform route, not unbounded source compilation. An interrupted download should be retried or resumed with checksum verification. Do not fall back to a robotic system voice, a paid API, or a silent “success.”

## Launch, verify, and reopen

For the minimal buildless website, store all playback assets inside the output folder using relative paths. Copy the packaged [local server](../scripts/serve_local.py) into the generated site folder as `serve_local.py`, alongside its README. This small standard-library helper supports the byte ranges browsers need for reliable audio seeking; no extra Python packages are required. From the generated site directory, run:

```sh
"/recorded/path/to/python3.12" serve_local.py --directory . --port 4327
```

Replace the placeholder with the recorded executable; if already on PATH, `python3.12` also works. On Windows use `& "C:\recorded path\python.exe" .\serve_local.py --directory . --port 4327` or the verified `py -3.12` launcher. Alternatively, from the extracted skill folder run `python3.12 scripts/serve_local.py --directory "../My Explainer/site" --port 4327`. Open `http://127.0.0.1:4327` in a browser. Keep that terminal running; stop it with Ctrl+C. If the port is occupied, choose another and use the same port in the URL. A `file://` tab is not the playback test. The helper binds to this computer's loopback address; it is not a public hosting service. Do not substitute bare `python -m http.server` without retesting seeking: its Python 3.12 behavior failed the in-app browser's audio-seek check.

Test a real first output, including play/pause, seeking, a scene boundary, the ending, captions, source access, and a phone-sized layout. Record visual inspection separately from listening and functional checks. Reopen it after stopping/restarting the server. Successful setup does not replace the other three quality criteria.

To move a finished site to another laptop, copy the whole site folder including recorded media, captions, content, `serve_local.py`, and the startup README. Replay needs only the browser and local server; it should not download models or call a provider. To create or revise narration there, rerun setup on that laptop. Python virtual environments are [not portable across locations/machines](https://docs.python.org/3/library/venv.html); do not package the original `.venv`, credentials, or personal caches as a transferable runtime.

Record the exact working interpreter, setup command, output path, server command, model/voice versions, and tested platform in the project's README. Keep fresh-setup results distinct from a reused developer environment. Document macOS, Linux, and Windows branches as tested, guidance-only, or unsupported according to evidence; one machine's success is not cross-platform verification.

Keep machine-specific paths and diagnostics local. Before publicly sharing a generated project, replace personal paths in startup instructions with portable placeholders and exclude runtime state, logs, caches, credentials, and private provenance. Serve only the dedicated finished-site directory.

## Optional live chat has its own setup

Seat-based authoring does not establish a website chat connection. Do not install a chat client when the user only needs the presentation. For a selected personal local subscription route, locate the actual executable, verify its version and active authentication, and check that the provider documents the intended integration:

- **Codex:** run `codex --version` and `codex login status`. If absent/broken, use the OS-specific native installation or repair route in the [official CLI guide](https://learn.chatgpt.com/docs/codex/cli); it does not require assuming npm or Homebrew. `codex login` opens subscription sign-in. Verify ChatGPT authentication, not API-key authentication, following the [authentication guide](https://learn.chatgpt.com/docs/auth?surface=cli).
- **Claude Code:** run `claude --version`, `claude doctor`, and `claude auth status --text`. Follow the [official native setup guide](https://code.claude.com/docs/en/setup) if missing/broken, then `claude auth login` for the user's eligible existing account. Verify the actual selected credential and [authentication precedence](https://code.claude.com/docs/en/authentication); a present API key or other configured provider can override subscription sign-in. Do not infer a supported embedded integration from CLI sign-in alone.

Never print credentials or package them with the site. Keep personal automation local; do not expose the account to public visitors. Before calling chat connected, send a real question with the article available and verify the answer plus its source citation, then perform [the remaining chat checks](experience-and-chat.md#checks). If this cannot run within the no-cost rule, retain the honest unavailable state and adjacent host-chat option. Report **presentation playback**, **narration quality**, and **embedded chat** separately; one working feature does not prove the others.

## Platform evidence

| Platform | Evidence and remaining check |
| --- | --- |
| Apple Silicon macOS 14+ | Fresh bootstrap, installation, offline synthesis, reuse, and browser seek/reopen passed on macOS 26.6.2 with uv 0.13.9 and CPython 3.12.16. macOS 14 is the wheel compatibility floor. See the packaged [verification record](setup-verification.md). |
| Windows x64 | Official CPU-wheel availability verified; setup/PowerShell commands documented, not executed on Windows. Require local installation and smoke success. |
| Linux x64, glibc 2.28+ | Official CPU-wheel availability verified; setup commands documented, not executed on Linux. Require local installation and smoke success. |
| Intel Mac, Windows ARM, Linux ARM/musl, other profiles | Current pinned helper does not cover these. Inspect available compatible CPU packages and validate a separate isolated profile before promising fresh narration; finished recorded sites still use ordinary browser playback. |

This records evidence as of November 22, 2026. It is not a promise that every future host version or package combination works. Follow current official installation guidance when the host differs, and record the result actually tested.
