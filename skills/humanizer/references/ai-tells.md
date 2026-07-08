# AI tells — the full catalog (prose + code), with fixes

Hunt these when de-slopping. The goal is honest, clear writing that happens to read like a competent human wrote it — **not** disguising authorship where disclosure is required. Match the user's own voice sample when you have one.

## Prose — vocabulary tells

| Tell | Examples | Fix |
|---|---|---|
| AI-vocabulary | delve, leverage, utilize, tapestry, landscape, realm, testament, underscore, showcase, boasts | plain verbs: use, dig into, show, has |
| Significance inflation | "pivotal", "groundbreaking", "in today's fast-paced world", "at the end of the day" | cut, or state the specific fact |
| Promotional adjectives | seamless, robust, vibrant, cutting-edge, powerful, comprehensive, rich | delete or replace with a concrete claim ("handles 10k rows") |
| Hedge/filler | "it's worth noting that", "it's important to remember", "generally speaking" | delete; say the thing |
| Vague attribution | "experts say", "studies show", "many believe" | cite a specific source or cut |
| Chatbot artifacts | "Great question!", "Certainly!", "I hope this helps", "Let's dive in" | delete entirely |

## Prose — structure tells

- **Rule of three everywhere**: "fast, reliable, and scalable." Vary the count; sometimes one adjective is stronger.
- **"It's not just X, it's Y"** and "It's not about X; it's about Y." — the signature AI antithesis. Rewrite as a direct claim.
- **Uniform paragraphs**: every one 3 sentences. Real writing varies rhythm — mix a one-liner with a longer thought.
- **Em-dash overuse** and the parenthetical-aside habit. Keep a couple; convert the rest to periods or commas.
- **Bulleted lists where prose belongs**: if the items are a flowing argument, write sentences.
- **Bold-word-per-line** lists that bold the first two words of every bullet regardless of emphasis.
- **Tidy moral-of-the-story conclusion**: "In conclusion, X is a powerful tool that…" — end on a concrete next step or just stop.
- **Section headers with emoji** (🚀 Features, ✨ Getting Started) in technical docs.
- **Perfectly balanced "on one hand / on the other"** that commits to nothing. Take a position.

## Code artifacts — comment tells

- Comments narrating the obvious: `i += 1  # increment i`, `# loop over users`. Delete; keep only WHY/gotcha comments.
- Docstrings restating the signature: `"""Takes a and b and returns the sum."""` on `add(a, b)`. Say the non-obvious (units, edge behavior, why) or drop it.
- Ceremony headers: `# ==== HELPERS ====` walls in a 40-line file.
- TODO theater: `# TODO: add error handling` with no ticket, left forever.

## Code artifacts — naming & shape tells

- Over-generic names: `data`, `data2`, `result`, `temp`, `ManagerHelper`, `Utils`, `handleData`. Use the domain word (`invoices`, `retryBudget`).
- Needless abstraction: an interface with one implementation, a factory for a thing constructed once, a config layer for two constants.
- Defensive noise: try/except that catches, logs, and re-raises unchanged; null checks on values that can't be null.
- Emoji/hype in commit messages: "✨ Enhanced functionality and improved robustness" → say what changed and why: "Cap retries at 5 so a dead upstream can't hang the worker."

## README / docs tells

- Badge walls (10 shields.io badges before the first sentence).
- "Features" section that's marketing, not capabilities ("Blazingly fast! 🔥").
- Empty "Contributing"/"Roadmap" boilerplate no one will follow.
- Generic install steps that don't match the actual project.

## Do NOT overcorrect

- Plain, polished writing is not proof of AI — don't inject typos or fake casualness to "prove" humanity.
- Keep technical precision. Never trade a correct term for a folksier vague one.
- Some structure is good: real docs use lists and headings. Remove the *reflexive* patterns, keep the useful ones.
- Preserve the author's meaning exactly. If a rewrite changes a claim, you've gone too far.

## Method

1. If the user gave a voice sample (2-3 paragraphs of their own writing), match its rhythm, vocabulary, and formality — not a generic "clean" voice.
2. Rewrite. Then self-audit: reread asking "what still smells generated?" and do a second pass.
3. Deliver the rewrite, then a short **Changes** list grouped by tell, so the user learns the patterns and can self-edit next time.
