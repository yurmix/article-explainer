# Optional free local English narration

Use the packaged [setup helper](../scripts/setup_local_narration.py) to prepare an isolated speech runtime. It needs a compatible Python interpreter; start with [first-run setup](first-run.md) when Python is absent. Neither helper calls a model API, uses API credits, activates an offer, or changes the global Python environment. Downloading public software and model weights is a one-time setup step; synthesis then runs locally.

## Inspect before installing

The executable used to run setup must be **CPython 3.12**. The helper uses that interpreter to create its private environment; it does not search for another Python, use uv, require Homebrew, or depend on files from the authoring machine. Replace the paths below with the selected interpreter, skill directory, and project directory. Keep quotes around paths containing spaces.

```sh
python3.12 path/to/article-explainer/scripts/setup_local_narration.py check --project-dir "my explainer project"
python3.12 path/to/article-explainer/scripts/setup_local_narration.py plan --project-dir "my explainer project"
python3.12 path/to/article-explainer/scripts/setup_local_narration.py install --project-dir "my explainer project"
```

For PowerShell, invoke a chosen executable with `&`:

```powershell
& "C:\path\to\python.exe" "C:\path\to\article-explainer\scripts\setup_local_narration.py" plan --project-dir "C:\work\my explainer project"
& "C:\path\to\python.exe" "C:\path\to\article-explainer\scripts\setup_local_narration.py" install --project-dir "C:\work\my explainer project"
```

`check` and `plan` are strictly local and read-only: they do not create the chosen project directory, install packages, download anything, synthesize speech, or execute the project's interpreter. Installed versions are inspected as data. `check` exits 0 when the recorded installation and smoke evidence are valid, or 2 when incomplete. `plan` explains the profile, destinations, packages, sources, and disk requirement. Only `install` changes files or uses the network. After inspecting the plan, proceed when the user's request already authorizes free local setup; do not introduce another conversational permission gate.

For a preexisting nonempty runtime, `install` also requires `--trust-existing-runtime`. Use that flag only for an environment you created and trust: Python startup hooks and installed packages execute code, and an ownership marker or version metadata cannot prove they are safe. An agent may retain the flag for its own verified project within existing authorization. Use a fresh project directory for an unknown or inherited environment. Fresh setup needs no trust flag.

## Platform scope

| Target | Route and evidence |
| --- | --- |
| Apple Silicon, macOS 14+, CPython 3.12 | Fresh installation and offline synthesis passed on macOS 26.6.2 with CPython 3.12.16; see the packaged [verification record](setup-verification.md). The OS minimum comes from the pinned Torch and NumPy wheel tags, not execution on macOS 14. |
| Windows 10+ x64, CPython 3.12 | Official CPU Torch and native speech wheels are available. This profile has not been executed on Windows; setup must pass its real smoke test on that computer before being reported ready. |
| Linux x64 with glibc 2.28+, CPython 3.12 | Official CPU Torch and native speech wheels are available. This profile has not been executed on Linux; setup must pass its real smoke test there. Alpine/musl is not covered. |
| Intel Mac, other architectures, older OS/libc, other Python versions | The pinned profile is not compatible or has not been established. Inspect official CPU wheels, select a compatible isolated dependency profile, and validate actual synthesis before declaring support. Do not try the current large install blindly. Recent Torch releases lack a current Intel-Mac wheel; that route needs a separately tested older stack. |

On Windows, if the log identifies a missing Microsoft C++ runtime DLL, such as `VCRUNTIME140.dll` or `MSVCP140.dll`, open [Microsoft's supported Visual C++ Redistributable guidance](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) and download its [official X64 installer](https://aka.ms/vc14/vc_redist.x64.exe). Run the Microsoft installer, choose Install or Repair as offered, follow any operating-system prompt or requested restart, then rerun the same narration setup command. Do not download individual DLLs from other sites. This diagnostic-triggered system dependency is outside the private Python environment; setup does not install it silently. Windows execution remains unverified.

Linux distributions without Python's `venv`/`ensurepip` need the standard matching Python environment support or the private Python route in first-run setup. The installer does not use sudo or silently install system components.

The CPU-only [official PyTorch index](https://download.pytorch.org/whl/cpu/torch/) supplies Torch first, without dependencies. Then PyPI resolves the full pinned dependency set, including the installed CPU Torch's dependencies. `pip check` and actual synthesis catch incomplete or incompatible installations. The installer does not pull CUDA distributions.

A public PyPI metadata audit found CPython 3.12-compatible Windows x64 and Linux x64 wheel tags for 92 of the 93 other pinned packages. The sole exception is the known pure-Python `docopt` source package. This verifies file availability, not successful dependency resolution, native imports, or audio generation on those operating systems.

## What is installed

Persistent setup files are contained in:

```text
<project>/.article-explainer/narration/
  .venv/                 isolated Python environment
  models/                verified model, two voices, language-data wheel
  cache/                 project-local package/model caches
  logs/                  package-install and synthesis diagnostics
  smoke/input.json       small built-in test passage
  smoke/media/           actual speech and timing output
  smoke/verification.json
  provenance.json        sources, hashes, installed versions, platform, smoke evidence
```

The model and language assets total about **341 MB**. Runtime packages and temporary package downloads need additional space; keep **3 GiB free** for setup. Depending on the platform and network, initial download can take several minutes. No Node.js, ffmpeg, system espeak installation, paid service, or API key is required for this WAV narration route.

The installer pins the complete tested runtime package set. Principal versions include Kokoro 0.9.4, Misaki 0.9.4, Torch 2.15.0 (or 2.15.0+cpu), Transformers 5.24.0, SoundFile 0.14.0, NumPy 2.5.5, spaCy 3.8.18, espeakng-loader 0.2.4, and English language data 3.8.0. Exact transitive pins are in the setup script and installed versions are saved in provenance. It requires binary wheels except the known pure-Python `docopt==0.6.2` source package; it does not launch a native compiler when a platform wheel is missing.

Public assets come only from the official [Kokoro-82M repository](https://huggingface.co/hexgrad/Kokoro-82M), its voice files, and the [spaCy model release](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0). Kokoro v1.0 uses Apache-2.0 weights. Every model, config, voice, and language wheel is checked against its pinned SHA-256 before use. The source URL, expected length, and complete hash are embedded in the setup script and written to provenance. No models, environments, or caches should be included in the transferable skill ZIP.

## Recovery and repeated runs

The bundled pronunciation engine has a short native data-path limit. Deeply nested project folders can exceed it even when every dependency is installed. The renderer handles this automatically: when needed, it copies the installed pronunciation data to a short private temporary folder, verifies the copy byte for byte, uses it for rendering, and removes it afterward. It does not install a system voice or download extra assets. If the temporary directory itself is too long, follow the diagnostic by selecting a short writable `TMPDIR` on macOS/Linux or `TEMP` on Windows, then rerun. This recovery was exercised in the fresh environment; pronunciation processing still feeds the neural narrator.

Rerun `install` after an interruption, adding `--trust-existing-runtime` when resuming your own nonempty runtime. Verified files are reused. Partial files are resumed only when the server's byte-range response matches the requested offset; an ignored range safely restarts that asset. Files are atomically promoted after the complete checksum matches. Transient downloads receive at most three attempts per run. A changed remote file cannot silently replace a pinned asset.

Within a setup directory the helper created, rerunning can complete an empty interrupted environment. It can also repair missing pip using Python's bundled `ensurepip` in an otherwise valid runtime that you explicitly trust. A nonempty, structurally incomplete runtime is rejected; choose a fresh project directory instead of overwriting it. Reuse requires the recorded base interpreter and Python version to match the environment. Fresh creation, empty interrupted-environment completion, and trusted missing-pip repair were exercised locally without network access.

An existing unrecognized setup directory is left untouched; choose another project directory or inspect it before deciding how to recover it. A concurrent installer receives an explicit lock error. Existing user projects and accepted narration are not overwritten by setup.

For a certificate failure, fix the trusted certificate chain; never disable TLS verification. The helper adds the fresh venv's pip CA bundle, avoiding a hidden global certifi prerequisite. An organization-managed network can supply a trusted bundle with `--ca-bundle "path/to/approved-ca.pem"`. Package configuration and inherited alternate pip indexes are neutralized, so an unrelated private mirror or token is not a prerequisite. Logs remain in the project for diagnosis.

A checksum or range-verification failure is different from a connection failure: keep verification enabled and inspect the official asset and pinned release before retrying. An unavailable asset, denied public download, rate limit, TLS failure, and local disk error receive distinct diagnostics. Errors omit redirected signed URLs and request headers.

If a pinned package is unavailable for the detected platform, explain the exact package and wheel limitation from the log. A separately researched free local profile is a valid next iteration; automatic paid fallback is not.

## Render an article after setup

The final setup report prints the private interpreter's absolute path. Use it to run the packaged [renderer](../scripts/render_local_narration.py). Its model directory is the setup directory's `models/` folder. Use forward-slash POSIX paths on Mac/Linux or quoted Windows paths with PowerShell's `&` invocation.

```sh
"my explainer project/.article-explainer/narration/.venv/bin/python" path/to/article-explainer/scripts/render_local_narration.py --input content.json --output media --model-dir "my explainer project/.article-explainer/narration/models" --samples --gap 0
"my explainer project/.article-explainer/narration/.venv/bin/python" path/to/article-explainer/scripts/render_local_narration.py --input content.json --output media --model-dir "my explainer project/.article-explainer/narration/models" --voice af_heart --speed .93 --gap 0
```

On Windows the private executable is `.venv\Scripts\python.exe`. Input is JSON with `scenes`, each containing a unique `id` and nonempty spoken `script`. Only American English has been validated. Use paragraph-sized passages; the model's documented weaknesses include very short utterances and rushed long utterances.

Sample mode renders the first scene with Heart and Bella. Full mode produces each scene WAV and a concatenated `narration.wav`. Every scene already has 0.18 seconds of head silence and 0.35 seconds of tail silence; keep additional gap zero so per-scene and combined playback share one timeline. The helper explicitly sets `model.eval()` and records actual audio durations. Do not add unrecorded player gaps.

The renderer verifies the packaged configuration, model, and selected voice hashes before loading them. Arbitrary substitute model files are unsupported by this helper; a different model requires a separately reviewed profile. Keep the complete skill folder together so these integrity checks remain available.

## Quality and verification limits

A successful setup smoke test proves that dependencies import, synthesis runs offline, nonempty mono 24 kHz speech is produced, waveform peaks are not clipped, hashes match, and timing data is plausible. It does **not** establish that the narrator is pleasant. Listen to a representative article sample before committing to the whole piece. If the agent cannot hear audio, show the sample to the user and record that scope honestly. A robotic system voice remains below the quality bar.

`timings.json` records model/package versions, input/script/audio hashes, sample-count durations, cumulative scene start/end, and token cues derived from Kokoro's predicted phoneme durations. These are not independent forced alignments; spot-check semantic transitions during playback. A metadata-only change to content JSON can change its whole-file hash while the per-scene script hashes still match. New voice settings or a newly rendered sample require a fresh listening assessment.
