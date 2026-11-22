# Optional skill composition and host adapters

## Resolve at runtime

There is no universal cross-host skill-import mechanism. Reuse means discovering a relevant installed skill, reading its entrypoint and necessary references, and following it for a bounded task. Do not copy its implementation into this package, invent a tool named after a skill, or assume names resolve on another host.

1. Inspect the host's advertised skill catalog and connected tools. Search by capability as well as name; plugin prefixes differ.
2. Select the smallest useful set. Read only skills needed at the current stage.
3. Record selected skill names, resolved locations/providers, and versions when available in the project's dependency notes. Do not put machine-specific locations in this portable skill.
4. Check required providers, paid calls, input/output contracts, permissions, and review gates. Explicit user constraints take priority. If a dependency requires an incompatible workflow, select another route; do not claim to follow it while bypassing its contract.
5. If absent, use the fallback below or the host's normal skill/plugin discovery. Follow installation rules and existing authorization. A matching name is not sufficient reason to fetch and execute an arbitrary package. For the standalone route, follow [first-run.md](first-run.md): no optional skill or plugin is required to author plain HTML/CSS/SVG, run the packaged local narration helper, or serve the result locally.

Installed skills are instructions, not automatic delegation to other agents. This skill does not require subagents or separate chats.

## Capability map

| Work | Known optional skill(s) | Compatibility and fallback |
| --- | --- | --- |
| Source ingestion | Host PDF/document/browser skills | Accessible text and original figures; disclose missing sections |
| Narrated explanatory video | HeyGen `faceless-explainer` | Requires HeyGen speech. Use when that route and its reviews fit; otherwise follow this skill's independent contracts |
| Narrated picture story | HeyGen `picture-video` | Requires HeyGen speech and image tools; images may cost credits. Not the default free-first route; its still-picture contract is not animated footage |
| Spoken script | HeyGen `script-writer` | Supply the source claim map and chosen form. Short-format defaults must not silently replace article coverage |
| Voiceover | HeyGen `narrator` | Use only with real HeyGen tools and authorized allowance. Otherwise a suitable local neural voice or another permitted provider must pass the same actual listening standard; do not claim it is the HeyGen workflow |
| Animation, captions, MP4 | HeyGen `motion-graphics`, `captions`, `video-editing` | Read specific contracts. Fallback: supported web animation and local media tools |
| Programmable video | Remotion `remotion-best-practices` and relevant create/render skills | Optional; verify license eligibility and runtime. Plain web scenes and local encoding are valid alternatives |
| Images | Native image-generation skill or provider-specific image skill | Available allowance and tool rules; fallback to provided/licensed assets and accurate diagrams |
| Website/hosting | Sites or another host web-development/artifact-routing skill | Preserve user's publishing rules. Portable source/local preview is the fallback; local files do not provide a publicly reachable backend |
| Model integration | Host provider documentation; setup skill only for the selected route | Check supported seat-backed/local routes first. Use API setup only when an API integration is selected and authorized |

Catalog reference: [Remotion official agent skills](https://www.remotion.dev/docs/ai/skills). Discover HeyGen and host-specific skills in the actual catalog; a subscription does not install skills. Do not assume provider web, API, and plugin plans have identical allowances.

## Codex primary adapter

- Use installed Sites instructions for website implementation when appropriate, and native image/media tools where available. Honor user/organization publication restrictions even when a dependency normally auto-publishes.
- Use official OpenAI documentation to verify supported subscription-authenticated local execution, such as Codex non-interactive mode, before treating an API as necessary. Check current [authentication](https://learn.chatgpt.com/docs/auth) and [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) documentation; availability and a working local client must still be verified.
- When an OpenAI API integration is actually selected, use the available API key/setup skill before implementing it. Do not load API onboarding merely because Codex is authoring the website. Honor applicable host instructions; if a dependency's setup gate conflicts with the selected no-API design, choose a compatible implementation route. Keep keys in the supported secret store, not project source.
- Prefer actual connected provider tools over guessed API calls; use local file/render/browser tools for implementation and review within their documented constraints.
- Open the result in the app when useful and supported. Do not treat opening a preview as evidence that all runtime behavior works.

## Claude adaptation

`SKILL.md` and relative references carry the workflow. `agents/openai.yaml` is optional Codex UI metadata, not a Claude dependency. No Codex namespace, personal directory, account ID, or credential is needed by the core instructions.

Adapt tool and hosting choices to Claude Code, Cowork, or chat separately. Shell-capable hosts can implement and run a project; restricted hosts may only generate files or use supported artifacts. If a backend cannot run there, deliver a runnable project and identify the missing capability rather than substituting fake chat. Do not constrain Codex to this restricted-host fallback.

Preserve seat-first authoring and optional API usage in the Claude adaptation. Independently verify whether the particular Claude surface supports subscription-authenticated automation for the intended use; neither a Claude subscription nor an SDK name proves this entitlement. If unsupported, retain local media/website production and report the chat options without importing Codex authentication assumptions.

Copying instructions does not transfer optional skills, accounts, media rights, or hosting. For explicit Claude adaptation and realistic test requests, use the [transfer brief](../TRANSFER.md).
