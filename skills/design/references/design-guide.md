# Design guide — make it distinctive, not defaults

The job is a small, fast, genuinely *designed* page — not the generic AI look. Derive every choice from the project's own subject.

## Escape the AI-default look

These read as "an AI made this" — avoid unless the subject truly calls for them:

- The cream/off-white background + serif body + terracotta/orange accent combo.
- Near-black background + one acid/neon accent (electric green, hot magenta) as the whole identity.
- Purple→blue 45° hero gradient with a big centered headline and two rounded buttons.
- Glassmorphism cards everywhere; emoji as section icons; "✨ Features" hype.
- Inter/Poppins for literally everything.

Instead: pick a concept from the project itself (a database tool can lean technical/monospace; a recipe app can lean editorial/warm) and commit to it.

## Color — build a small system

- Choose 4–6 named hexes: 1 background, 1 primary text, 1–2 accents, 1 muted/border. Derive from the subject, not a default.
- Ensure contrast: body text ≥ 4.5:1 on its background, large text ≥ 3:1 (WCAG AA). Check it.
- Support light **and** dark via `prefers-color-scheme` unless you deliberately commit to one look.
- One accent does most of the work; a second is a rare highlight. More than two accents = noise.

## Type — one pairing, real hierarchy

- A display face for headings + a readable body face. System stack (`system-ui`) is free and instant; or one Google Font pair, self-hosted or `<link>`-ed.
- Establish scale (e.g., 3rem / 1.5rem / 1rem) and stick to it. Line-height ~1.5 for body, tighter for display. Max line length ~66ch for readability.

## Layout & the signature element

- Mobile-first, fluid; test at 360px and 1440px. Generous whitespace beats cramming.
- Pick **one** signature element that makes the page memorable: a distinctive hero treatment, an animated diagram, a clever nav, a typographic masthead. One — not five.
- Respect `prefers-reduced-motion`; keyboard focus must be visible; images `max-width:100%`.

## Build & ship

- Single self-contained `index.html`, inline CSS/JS, no build step, real project content (never lorem ipsum).
- Put it in `docs/` of the existing repo (GitHub Pages "deploy from branch"), or a `gh-pages` branch. **Never create a new repo** for an existing project's site.
- Preview locally (`python3 -m http.server` in the folder). Deploy only after explicit consent to the exact command; `scripts/gh_pages_deploy.sh` handles gh-CLI or plain-git and prints the URL.

## Pre-ship checklist

- [ ] Contrast AA on all text · [ ] keyboard focus visible · [ ] reduced-motion honored
- [ ] responsive at 360 / 768 / 1440 · [ ] no external calls that break offline · [ ] real content, no lorem
- [ ] doesn't look like the AI defaults above · [ ] copy run through `/humanizer`
- [ ] page `<title>`, meta description, and favicon set
