---
name: design
description: Design a quick, distinctive static website for the current project and deploy it to GitHub Pages (free hosting). Use whenever the user wants a landing page, project site, demo page, docs site, portfolio page, to "put this online", "deploy a site", or mentions GitHub Pages. If the user is inside an existing project/repo, add the site to that repo — never create a new repository for it.
---

# Design (+ GitHub Pages deploy)

Build a small, fast, genuinely designed static site and deploy it free on GitHub Pages. Read `../_shared/GUARDRAILS.md` first.

## Rules that override everything
- **Existing project?** (`git rev-parse --is-inside-work-tree` succeeds) → the site goes INTO this repo (usually `docs/` for Pages "deploy from branch", or a `gh-pages` branch). Never create a new repo for an existing project.
- **No project?** Ask before creating anything, and scaffold locally; the user pushes.
- **Consent gate:** never run `git push`, `gh repo create`, or enable Pages without the user explicitly saying yes to the exact command. Show the command first.

## Workflow
1. Gather in one round: what the site is for, one-line pitch, 2-4 sections needed, any brand color/logo, target repo.
2. Design before code: pick a palette (4-6 named hexes), a display+body type pairing (system or Google Fonts), a layout concept, and ONE signature element that makes this page memorable. Avoid the generic AI look (cream background + serif + terracotta accent, or near-black + acid green). Derive choices from the project subject itself.
3. Build a single self-contained `index.html` (inline CSS/JS, no build step, responsive, keyboard focus visible, honors prefers-reduced-motion). Put it in `docs/` of the target repo (or `site/` if user prefers). Use real project content, not lorem ipsum.
4. Open it locally for the user (`python3 -m http.server` or just the file path) and iterate.
5. Deploy (only after explicit yes): run `scripts/gh_pages_deploy.sh` from this skill folder — it uses `gh` CLI if present, else plain git, and prints the final URL. For repo `user/repo` with `docs/` on main, the URL is `https://user.github.io/repo/`.

## Output format
End with: site file path, local preview command, exact deploy command awaiting consent, and expected live URL.

## Chaining
- Input: project repo, optionally a REPO_MAP.md from tools/repo_map.py for content.
- Output: docs/index.html + live URL; pair with /humanizer to de-AI the copy, /critical-review for a design audit.
