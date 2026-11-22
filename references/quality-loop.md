# Quality and learning value

## Four acceptance criteria

**Visuals:** the rendered result has a deliberate, appealing composition, readable labels, and a clear focal point. Scenes demonstrate relationships or consequences with purposeful variation. Apply the concrete visual checks in [visual-design.md](visual-design.md). A functioning interface is not evidence of compelling design.

**Voice:** narration sounds natural and pleasant at a comfortable pace, with meaningful phrasing and emphasis. Mechanical rhythm, distracting pronunciation, unnatural joins, and rushed or monotonous delivery fail. Use the audition and listening process in [budget-and-media.md](budget-and-media.md). Intelligibility alone is insufficient; an installed system voice is not an acceptable default merely because it is free.

**Content:** the viewer can explain the central argument, its mechanism, and an important limitation in plain language. Remove generic hooks, grand claims, repetitive conclusions, abstract noun chains, filler transitions, and sentences that sound fluent without teaching anything. Prefer concrete verbs and examples, define necessary terms on first use, and give each sentence a useful role. Concision means low effort to understand, not the fewest words at any cost.

**First-time portability:** a new user on another laptop can start from this package, identify a supported route, install its justified prerequisites, verify a small real output, and open/reopen the resulting explainer. Prior conversation, personal paths, the author's caches, and other installed skills are not prerequisites. Read [first-run.md](first-run.md). Account entitlements and operating-system restrictions remain real capabilities to check, not things that travel inside a ZIP.

## Verify first-time setup

Test the packaged instructions in an empty directory, including a path containing spaces, with a separate environment and cache. Do not make the test pass by silently borrowing the author's virtual environment, model files, credentials, or globally installed optional tools. An evaluator follows the documented setup, runs a real smoke synthesis, checks repeated setup/recovery, and serves a local output using the documented command. Include a no-Python branch in the guide even if the test host already has Python.

For each recommended dependency, document its purpose, official installation source, supported platform/version constraints, expected disk/network needs, verification command or sample, and a specific remedy when installation fails. Keep unnecessary video/rendering stacks out of a web-only route. Test exact published commands where the host permits. Distinguish clean-environment testing on one OS from execution on another OS, another physical laptop, or Claude; document untested targets explicitly. A successful install alone does not pass narration or teaching quality.

## Add understanding rather than just shorten

Choose a small set of source-grounded learning outcomes before writing. Use visuals or interactions to make a difficult distinction observable: change one condition, predict an outcome, compare two cases, or trace a consequence. Clearly label added hypothetical examples; do not imply they are the author's evidence.

Have a reviewer answer transfer questions using the finished experience: explain the distinction, apply it to a new case, and identify when the rule or analogy stops working. Check whether the narration and visual states actually support those answers without rereading the article. Record the concrete teaching advantage over text-only presentation. This is an expert assessment of likely learning value, not proof that real users learn better; do not claim a human learning study occurred.

Preserve the source's qualifications and follow applicable reuse limits. More attractive presentation must not make an uncertain claim sound settled. Article-grounded chat cannot repair an opaque or misleading main explanation.

## Iterate on observed failures

For an explicitly requested iteration loop, use a producer and a separate reviewer when subagents are available and authorized. Give the reviewer the source, user criteria, and actual deliverable without an intended verdict. The reviewer inspects rendered screens, meaningful playback states, the complete script, and actual audio where supported. The producer repairs specific failures; the reviewer rechecks affected states and important regressions. Preserve accepted work instead of repeatedly starting over.

Keep a compact record per version: artifact location, source/script/audio versions, inspected evidence, each criterion's pass/fail/unverified status, and remaining defects. A plan, screenshot alone, or clean test log cannot pass all criteria. Model/provider reputation and audio metrics cannot establish that narration is pleasant.

Mute media elements before automated functional playback tests so test runs do not unexpectedly play through the user's speakers. Leave the user's system volume alone. Muted playback can verify controls, seeking, timing, and ending behavior; it cannot verify sound quality. Use a genuinely supported private audio-perception tool for listening when available. Otherwise preserve the explicit listening gap and present an intentional audition only when needed for the user's review. Do not change the finished site's normal user-initiated playback to accommodate silent tests.

Honor the user's current resource ceiling throughout. Under an explicit seat-only/no-API instruction, do not use even promotional API credits, activate offers, buy extra seat capacity, or request paid resets. Preserve progress at normal seat limits and resume only when ordinary allowance becomes available. Do not silently replace a difficult verification task with a paid service.

When a capability is unavailable, complete other useful work and investigate supported free alternatives. Describe the remaining gap accurately; seek a user listening judgment only if actual auditory assessment cannot be performed by the available tools. Continue iteration while meaningful progress is possible, and do not mark success merely because a turn ended or many attempts were made.
