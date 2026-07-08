---
name: skill-suggestions
description: From a coarse or vague prompt, work out what the user is trying to do and suggest the best skills to fast-track it — top 5 max unless asked for more, plus 1-2 generic always-useful skills. Use whenever the user asks "which skill should I use", gives a broad goal without naming a skill, seems unaware a relevant skill exists, or asks what skills are installed. Can also search online for better skills.
---

# Skill Suggestions (the router)

Match intent to skills without overwhelming the user. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. **Inventory** — run `python3 scripts/inventory.py` (add `--all` for disabled, `--grep TERMS` to prefilter, `--json` to parse). It lists every installed skill with its trigger description and labels local vs external (gstack, anthropic-skills). This is cheaper and more reliable than `ls` + reading files; it also surfaces the ~50 external skills a plain `ls` would bury.
2. **Infer intent** from the coarse prompt: is the user researching, building, understanding, reviewing, deploying, automating, or lost? If genuinely ambiguous between two intents, ask ONE clarifying question.
3. **Rank and cap at 5** task-specific skills (unless the user asked for more). For each: skill name, one line on why it fits THIS request, and the literal invocation (`/skill-name ...`). Prefer an installed match (local or already-synced external) over anything you'd have to fetch.
4. **Add 1-2 generic skills** that help in almost any session (e.g., /guide for navigating the repo, /control-skill to bake project conventions in) — clearly labeled "generic".
5. **Optionally look online** (say you are doing it): if nothing installed fits, check well-known catalogs — github.com/anthropics/skills, github.com/garrytan/gstack, skills.sh, awesome-claude-skills lists. NEVER auto-install: present name, repo link, what it does, and offer to add it as a source (`/firecrawl` or the skill manager's Sources panel → `skillsource.py`) so it installs cleanly and stays read-only. Free, reputable sources only.
6. If nothing fits, say so and suggest /i-have-no-idea or building a new skill.

## Output format
"You seem to be trying to: [intent]." Then a 5-row max table: Skill | Why for this task | Invoke. Then "Generic: ...". Then online finds (if any) awaiting consent.

## Chaining
- Input: any vague request. Output: a routed plan; commonly chains into /skills-interleave to combine the chosen skills.
