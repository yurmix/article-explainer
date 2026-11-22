---
name: article-explainer
description: Turn an article into a faithful narrated explainer website with animated visuals, a readable source, and source-grounded chat; optionally produce a standalone video. Use for article-to-explainer production and revisions, with free-first or budgeted enhanced modes.
---

# Article Explainer

Create an explanation a skilled author could plausibly have chosen: preserve the article's argument, evidence, tone, and important qualifications while adapting it for speech and visual understanding. Do not claim author approval or imply that a synthetic narrator is the author.

The default product is a responsive website with a narrated animated presentation, the readable article, and a question sidebar grounded in that article. Standalone video is an alternative or optional export, not a mandatory extra deliverable. Honor a request for only a video, a plan, or a skill without building unrelated outputs.

Codex is the primary integration target. Use its strongest available tools; portability must not reduce quality to the least capable host. The editorial and production contracts are portable. Claude may adapt the execution/hosting layer using the [transfer and testing brief](TRANSFER.md).

## Defaults and independent choices

| Choice | Default | Alternatives |
| --- | --- | --- |
| Editorial form | Faithful adaptation | Verbatim when wording is essential; short summary when explicitly wanted |
| Presentation | Animated web scenes with recorded narration | Embedded video for footage-led stories; mixed web scenes and clips |
| Spending | Free-first: existing seat allowance and free local tools; no extra charges | Enhanced: a user-authorized cap and identified benefit |
| Chat | Answers about the full source, with passage links | Explicitly labeled outside context when requested |
| Publication | Follow the user's destination and applicable publishing rules | Local preview/package while hosting or publication is unresolved |

Free-first and enhanced use the same fidelity and review standards. Payment buys possible improvements in voice, assets, capacity, or convenience, not guaranteed excellence. Do not shorten an argument merely to meet a free allowance, and do not assume that paying is necessary for good narration.

The acceptance standard has four parts: compelling visuals; pleasing narration that is easy to follow; concise understandable content that gives the viewer a clearer mental model than an ordinary article summary; and self-contained first-time setup on another laptop. Robotic narration, generic diagram repetition, vague polished-sounding prose, or undocumented dependencies fails this standard. Use the checks in [quality-loop.md](references/quality-loop.md); free-first does not lower the acceptance bar.

Separate authoring from runtime. Creating the skill, analyzing the article, writing code, and producing local assets do not inherently require a model API. Live website chat needs its own verified execution route. A subscription may support personal local automation without covering a public website's visitors. Quality mode and chat deployment are separate choices.

## 1. Resolve inputs and capabilities

Reuse information already supplied. Obtain the full accessible article, including meaningful figures and captions; a search snippet is not the source. Ask for accessible text if retrieval is incomplete. Resolve audience, language, approximate length or hard limit, intended use, and voice/style preferences only when needed. Otherwise state sensible assumptions and proceed with reversible work. With no article, ask for it and prepare only independent setup; do not fabricate an author's article.

On a first run or a different laptop, read [first-run.md](references/first-run.md) before selecting dependencies. Detect the actual OS, execution access, installed tools, and available seat capabilities. Choose the smallest adequate route, explain why an installation is needed, and provide or execute its complete setup and verification within the user's authorization. Do not assume the original author's software, caches, accounts, optional skills, or previous conversation. Self-contained means the package carries the setup knowledge and helpers; large public models and runtimes may be downloaded through its documented installation route.

Read [dependencies.md](references/dependencies.md) to discover and reuse installed skills. These are optional composition points, not automatic imports or guaranteed tools. Read a selected dependency before doing its work. Resolve tools, accounts, execution, rendering, audio inspection, and hosting capabilities on the actual host; do not assume Codex and Claude expose the same ones.

Read [budget-and-media.md](references/budget-and-media.md) before synthesis, image generation, or selecting a live chat provider. Resolve a no-additional-charge route before proposing API setup: current seat for authoring, suitable local media tools, and supported subscription-backed or local-model chat where available. For websites, use the route selection in [experience-and-chat.md](references/experience-and-chat.md). Do not create keys/accounts, activate credit offers, subscribe, or spend merely to discover availability. Continue independent local work when a runtime connection is unresolved.

## 2. Make the editorial judgment visible

Read [editorial.md](references/editorial.md). Capture a versioned article with stable passage IDs, then map its thesis, reasoning, evidence, counterarguments, caveats, and conclusion. Choose duration from needed coverage and complexity. Distinguish faithfulness to the author's position from independently verifying its truth.

Create the complete spoken script and a compact scene plan. Show intended emphasis, significant omissions with reasons, provisional runtime, visual approach, selected mode, and any paid estimate. Link consequential claims and scenes to source passages in the working project. Keep narration separate from stage directions and pronunciation notes.

Use one combined script/scene review before quota-consuming narration unless the exact script is already approved or the user has explicitly delegated this review. Preserve any selected provider's stricter requirements. Continue reversible development while review is pending. Routine styling, timing, and local repairs do not need another approval; substantive changes to an accepted argument do.

When the user explicitly delegates iterative production and review, perform this review internally and continue within the authorized budget. Do not repeatedly ask the user to accept routine script, design, or voice changes in that loop. A required subjective listening judgment that the host cannot perform remains an honest verification gap.

## 3. Produce reusable assets and a presentation

Read [experience-and-chat.md](references/experience-and-chat.md) for websites and [budget-and-media.md](references/budget-and-media.md) for narration and optional video export.

Read [visual-design.md](references/visual-design.md) before implementing the visual experience. Choose a concrete art direction suited to the article, establish a clear hierarchy, and inspect representative rendered scenes before expanding the design. This is an agent-performed quality check, not another user approval gate. Free-first receives the same visual care as enhanced.

Create narration from accepted text, measure it, and align visuals and captions to actual speech. Prefer animations that demonstrate a change, relationship, or consequence over moving decorative labels. Accurate diagrams and source images can be more useful than generated footage.

Use a shared content package for either renderer: source passages, claim map, script, scenes, asset provenance, audio cues, and subtitles. Record source version and selected skills/providers. Keep credentials out of this package. A corrected scene should not require regenerating all accepted audio or assets.

## 4. Ground chat in the article

Give chat access to the full article or retrieval over it, not just the presentation script. Pass current scene, selected passage, and relevant conversation context. Require supported answers to identify source passages; distinguish inference, illustrative examples, outside context, and information absent from the article.

Implement a real provider connection when authorized and available. A mocked sidebar is not working AI chat. If chat cannot be connected, finish the independent presentation and source reader, label chat unavailable, and state the specific remaining prerequisite. Do not describe the overall requested product as complete while a required feature is missing.

## 5. Validate and deliver

Check source fidelity and the delivered experience. Review narration, animations, captions, and chat answers using available tools; disclose unavailable listening, playback, or browser checks. Do not equate successful rendering with audiovisual review.

Use [quality-loop.md](references/quality-loop.md) to assess all four criteria and repair observed failures. When the user asks for independent subagent testing, keep production and verification separate and run a fresh review of the actual revised output. Do not declare the goal achieved while any required criterion is failed or unverified.

Apply the visual review in [visual-design.md](references/visual-design.md) separately from functional tests. Inspect actual desktop/mobile renders for composition, hierarchy, legibility, clutter, and explanatory value; repair visible weaknesses before delivery. Working controls and absence of overflow alone do not establish design quality.

For web: verify play/pause/resume/seek, chapter changes, captions, passage links, mobile layout, keyboard access, and chat failure handling. For chat: test answerable, qualification-sensitive, out-of-source, and current-scene questions; inspect actual supporting passages. For video: check the final encoded file, audio, duration, and subtitle alignment.

Deliver the requested runnable website or playable video, reusable source, transcript/captions, article provenance, editorial omissions, selected dependencies, and verified limitations. Include the actual start/reopen commands, setup checks and any required runtime installation guidance for that deliverable. Follow host/user rules for publication and external data; a skill invocation is not a waiver of destination or audience restrictions. Install only dependencies justified by the selected task, within existing authorization and host permissions.
