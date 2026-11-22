# Free-first and enhanced production

## Plan from actual capabilities

Distinguish tools from installed skills, credits from subscriptions, and web-editor plans from API/plugin allowances. Inspect actual tools and relevant read-only plan information. Verify current quotas, models, prices, and output-use terms from providers; do not hardcode commercial prices here.

Explain costs by component: authoring under the current seat, one-time media production, repeat playback, live chat inference, and hosting. Creating an API key is not itself model usage, but permission to create a key does not authorize billable calls. Included or promotional API credits still use the API billing system; they are not unlimited seat usage. Do not activate/link a credit offer unless authorized, or assume an existing key or balance permits spending. Verify expiry, eligible services, and overflow behavior before relying on credits. If a no-charge cutoff cannot be assured, leave that route disabled and use a verified alternative or report the limitation.

Estimate from the final script and planned assets. Article length affects adaptation and chat context; narration allowance usually follows submitted text or output duration. Per-call limits and daily/monthly quotas are separate; splitting does not bypass total quotas. Include expected corrections. Retakes may consume allowance even if absent from the final result.

For English only, 130–160 spoken words/minute is a rough planning estimate; complex visuals may need more time. Other languages and styles differ. Actual audio decides final timing.

## Modes

**Free-first (default)**
- No new subscriptions, charges, paid overages, or automatic top-ups. Verified and authorized existing included entitlements may be used; distinguish these from universally free services.
- Prefer current-seat authoring and suitable local tools. Seat usage still has plan limits; stop or wait at those limits instead of purchasing extra capacity or falling back to a paid API. Do not introduce API setup as a prerequisite for script, diagram, website, or local video creation.
- Use permitted freemium speech/images where useful. Check allowance for the full planned generation and corrections where observable; unknown quota cannot support a promise of free completion.
- A tested local narration model is a sustainable fallback for long/frequent work. Kokoro is one candidate, not a required dependency; verify language coverage, model/software license, hardware, installation needs, and actual samples. Local compute still takes time and resources.
- For American English on a shell-capable host, this package includes an optional tested [local narration helper](local-narration.md). Read its prerequisites before selecting it. Reuse compatible existing local assets; do not bundle model weights or make this route a requirement for every host.
- Prefer a suitable local neural voice or an authorized no-charge provider voice that passes an actual audition. An operating-system voice may be used for a timing scratch track, but cannot be promoted to final narration unless its actual delivery meets the same naturalness standard. Robotic output is a failure, not a free-first compromise. Browser speech is an optional preview with variable voices/timing, not a substitute for tested recorded narration when synchronization or export is required.
- If free capacity is exhausted, wait for its ordinary allowance renewal or use an authorized compatible fallback. Never purchase or request an extra reset, rotate accounts to evade limits, or silently upgrade.
- Suitable existing images, accurate diagrams, and local animation/encoding avoid recurring asset-generation fees. Do not promise indefinite free hosting.

**Enhanced**
- Identify the specific benefit before spending: preferred expressive voice, better language delivery, consistent illustrations, useful footage, or throughput.
- Keep authoring on the existing seat where suitable. Enhanced media does not require API chat, and API chat does not establish enhanced media quality. Do not artificially degrade the free-first result or promise that payment guarantees excellence.
- Use an explicit user-authorized budget and scope; estimate assets/retakes and live chat separately. Enhanced is not unlimited spending.
- Preserve accepted assets and replace only defects or requested revisions. Judge quality on output rather than provider price.

Keep a small ledger: provider/model, estimated units/cost, actual usage when returned, remaining authorization, and unknown quotas. Stop before exceeding authorization. If exact hard caps cannot be enforced, use conservative request limits and explain the limitation.

## Narration

Choose real available voices from previews; never invent IDs. Use existing previews to shortlist candidates, then audition a short representative excerpt before full production, including difficult names/terms and a sentence needing emphasis. Reuse accepted script text where possible; respect applicable script, provider, and spending approvals. The user's delegated no-cost production loop authorizes ordinary local auditions. Do not consume paid quota for an audition without authorization.

Judge actual sound: natural rhythm, pleasing tone, intelligible pronunciation, meaningful pauses/emphasis, and absence of distracting synthetic artifacts. Test more than one suitable candidate when the first fails; do not polish a clearly robotic system voice with music or speed changes and call it fixed. A local neural model such as [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) is a candidate, not a guarantee; verify its supported language and actual output.

Record who or what listened, which audio was heard, and the specific observations. If the host cannot perceive audio, technical checks and transcription can find defects but cannot certify pleasantness. Provide the actual sample for user listening when that is the remaining verification requirement. A user's accepted sample establishes a voice preference, not proof that every later sentence and join was heard. Keep any unreviewed scope explicit. If every permitted voice fails, leave narration pending and explain the available choices rather than deliver a rejected voice as finished.

While listening judgment is pending, a clearly labeled candidate may be assembled with authorized free local synthesis to test timing and playback. This does not accept the voice or waive the listening check. Preserve the audition settings when extending an accepted sample; reassess difficult passages or any changed voice, pace, or delivery.

Select one accepted narrator for the piece. Finalize wording and check names, numbers, acronyms, units, and negations before full synthesis.

Prefer a coherent short take. Split longer scripts at semantic boundaries for provider limits or practical editing, keeping voice/settings consistent. Preserve originals and exact submitted text. Keep natural speed/pitch; revise script or visuals instead of accelerating speech to fit an arbitrary runtime.

For local neural synthesis, verify that the runtime actually uses inference/evaluation mode, record the model and voice versions, and prevent implicit provider calls when operating offline. A fixed random seed is not a substitute for evaluation mode. If a renderer correction changes audio after an audition, preserve the accepted recording and distinguish it from newly generated candidates.

Measure audio and use reliable provider timings or corrected alignment. Do not distribute words evenly to fabricate captions; phrase-level cues are acceptable when word alignment is unavailable. Listen for omissions, pronunciation, emphasis, joins, and tail truncation. Disclose unavailable listening.

Provider retry/approval gates apply. Reconcile unknown paid outcomes before another call. Do not silently switch narrator midway; use a coherent full-narration plan when a route changes. Switching services may change data permissions and terms.

## Visuals and finishing

Choose one visual language with purposeful variation. Prove it in representative opening, explanation, and conclusion scenes. Preserve literal accuracy for maps, charts, measurements, screenshots, and documentary images. Identify generated illustration when it might be mistaken for evidence.

Show a constraint, change a condition, demonstrate a consequence, and hold for comprehension. Keep one focal idea at a time; captions and diagrams must not compete. Use restrained transitions rather than effects at every boundary.

Prioritize voice clarity. Music is optional; use appropriately licensed/original material below narration. Do not pay for music by default. Recorded narration and assets should replay without generating new AI output each visit.

## Optional MP4

Use a supported local renderer/encoder or compatible existing video skill. Remotion is optional and requires license eligibility checks; Python/FFmpeg or another renderer can also fit.

Export accepted scene content against audio cues, with a deterministic path through interactions. A web presentation is not meaningfully exported by recording arbitrary clicks. Choose dimensions for the destination, normally 1080p when practical. Reuse audio and include subtitles/transcript.

Inspect final audio, dimensions, runtime, synchronization, and start/end. Review full playback with sound where possible. Keep editable source, assets/provenance, subtitle sidecar, dependencies, and reproduction instructions. Successful encoding alone is not an audiovisual or fidelity pass.
