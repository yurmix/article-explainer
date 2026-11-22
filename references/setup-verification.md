# First-run verification record

Verified November 22, 2026. An independent evaluator followed this package from a fresh folder containing spaces, with a newly downloaded private Python, separate caches, no inherited credentials, and no prior narration environment or model files. The corrected local setup and playback route passed on **Apple Silicon macOS 26.6.2, CPython 3.12.16, uv 0.13.9**.

This was an isolated setup on the existing Mac, not execution on a second physical laptop or a fresh operating-system installation. macOS 14 is the pinned wheels' compatibility floor, not an additional OS version tested.

## Executed checks

| Check | Result |
| --- | --- |
| No existing compatible Python | Official private uv bootstrap downloaded a new Python; managed/no-project/system selection excluded an ambient virtual environment |
| Read-only inspection | `check` and `plan` ran with networking denied, correctly reported incomplete setup, and did not create the target project |
| Fresh installation | Downloaded the pinned CPU runtime and all five model/language assets from their official sources; checksums passed |
| Real narration after repair | Generated 11.68 seconds of mono 24 kHz speech with 30 token cues while the OS denied networking |
| Native dependency isolation | Python packages and native libraries came from the new environment; no Homebrew or global Python libraries were borrowed |
| UTF-8 input | Separate offline synthesis with a curly apostrophe and em dash passed |
| Repeat installation | Passed offline in 2.33 seconds; all five assets reused, with asset and smoke hashes and modification times unchanged |
| Final readiness check | Exit 0, no dependency mismatches, ready=true |
| Local playback and reopening | The copied bundled server passed actual browser seek/play/pause; seeking passed again after stopping/restarting the server and reloading |

The first attempt exposed two defects that were repaired and retested:

1. A 241-character pronunciation-data path exceeded a native library's limit. The renderer now stages a verified temporary copy at a short path when needed. All 364 copied data files and the active native library were checked against the freshly installed originals; cleanup passed.
2. Python 3.12's basic HTTP server loaded the audio but prevented seeking in the in-app browser. The bundled `serve_local.py` returned the required partial responses. The browser then reported the full seekable duration, reached three seconds on request, and preserved its position on pause and after a server restart.

Additional component checks covered download verification/recovery, missing-pip and partial-environment repair, and 25 HTTP server cases. Those checks supplement the independent end-to-end test; they do not prove native execution on other operating systems.

Measured steady-state disk use was **1.701 GiB** for narration setup plus **0.116 GiB** for the private Python/uv bootstrap, approximately **1.817 GiB combined**. Peak temporary usage was not measured. Keep the documented 3 GiB free-space allowance and inspect the plan on the target laptop.

## Original first-run helpers tested

| File | SHA-256 |
| --- | --- |
| `setup_local_narration.py` | `8a1c373e49b4b3211a7e79e3912c96ad111a2c266bbfb4853f54b2fb4326e0a4` |
| `render_local_narration.py` | `e150becc9e6fea1c9a2271768935a534dce51d0e00a69c725a28160c37139a48` |
| `serve_local.py` | `9ba76014197f7717aa55ee7e73ef6cf22534e7d4f3ea971bdf0f594008a95f84` |

Smoke audio SHA-256: `d9fb98ee89c32eb631f921cc9a89d65841ce349a5b9398b4e1c81ebe30c04400`. This identifies technical evidence, not a listening approval.

## Public-release security follow-up

Later on November 22, 2026, code review found and repaired five issues: execution of project Python during read-only inspection, hidden files exposed through an index symlink, missing HTTP Host/origin restrictions, missing renderer asset verification, and unsafe log/output symlink writes. An independent reviewer then passed 22 focused server cases and 18 setup/renderer cases against these final helpers:

| File | SHA-256 |
| --- | --- |
| `setup_local_narration.py` | `50998ee60993f13a01fc00f09faa78160cc86bc7eb6e4d2c499b6a6e85046a64` |
| `render_local_narration.py` | `7ebb86e868fad23b84fec7bd7e1a2f05b19abb8a671d7c0d997c827c36a09c48` |
| `serve_local.py` | `7d334205a6ade612a6a727816667e0b36e759b4bc301f5485e8a33fa09cf2aa9` |

The revised renderer produced the same 11.68-second smoke audio and SHA-256 above with networking denied by the OS. This reused the independent first-run environment; the entire download/bootstrap sequence was not repeated after the security changes. Offline component checks also passed for fresh environment creation, completion of an empty interrupted environment, and missing-pip repair in an explicitly trusted runtime.

Muted browser seeking/playback passed with the initial HTTP restrictions. A subsequent change allowed explicitly activated top-level navigation from another page while preserving Host/Origin checks; the final 22 HTTP cases covered that exception and the normal audio paths. Browser playback was not repeated after that navigation-only change. The public repository also includes 10 server regression tests covering 53 requests, all passed on the reviewed Mac.

These helpers are for trusted local projects. Version metadata and an ownership marker do not make inherited Python code safe; nonempty runtime reuse requires explicit trust. Dependency installation still trusts third-party software, and the helpers are not a sandbox against concurrent malicious filesystem writers. Native testing on other platforms remains outstanding.

## Limits that travel with the package

Windows x64 and Linux x64 instructions were reviewed, and compatible package wheel availability was checked. Neither operating system was executed. Intel Mac and other unsupported profiles need separate compatibility work. Claude execution, new-session skill discovery, a new user's account entitlements, and embedded live chat were not validated by this setup test.

The smoke page tested installation and playback, not article design, learning value, or voice pleasantness. Muted functional tests cannot certify audio quality. A new production run still needs the four acceptance checks and actual listening; a successful installer is not a quality waiver. No model API inference, credits, purchases, top-ups, or paid resets were used.
