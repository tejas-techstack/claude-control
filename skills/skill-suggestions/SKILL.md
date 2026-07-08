---
name: skill-suggestions
description: From a coarse or vague prompt, work out what the user is trying to do and suggest the best skills to fast-track it — top 5 max unless asked for more, plus 1-2 generic always-useful skills. Use whenever the user asks "which skill should I use", gives a broad goal without naming a skill, seems unaware a relevant skill exists, or asks what skills are installed. Can also search online for better skills.
---

# Skill Suggestions (the router)

Match intent to skills without overwhelming the user. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. **Inventory** — list installed skills: `ls ~/.claude/skills` and `ls .claude/skills 2>/dev/null`. Read only names + the description line of plausible matches (token thrift).
2. **Infer intent** from the coarse prompt: is the user researching, building, understanding, reviewing, deploying, automating, or lost? If genuinely ambiguous between two intents, ask ONE clarifying question.
3. **Rank and cap at 5** task-specific skills (unless the user asked for more). For each: skill name, one line on why it fits THIS request, and the literal invocation (`/skill-name ...`).
4. **Add 1-2 generic skills** that help in almost any session (e.g., /guide for navigating the repo, /control-skill to bake project conventions in) — clearly labeled "generic".
5. **Optionally look online** (say you are doing it): check well-known catalogs — github.com/anthropics/skills, github.com/garrytan/gstack, skills.sh, awesome-claude-skills lists — for a skill that fits better than anything installed. NEVER auto-install: present name, repo link, what it does, and ask before fetching. Free, reputable sources only.
6. If nothing fits, say so and suggest /i-have-no-idea or building a new skill.

## Output format
"You seem to be trying to: [intent]." Then a 5-row max table: Skill | Why for this task | Invoke. Then "Generic: ...". Then online finds (if any) awaiting consent.

## Chaining
- Input: any vague request. Output: a routed plan; commonly chains into /skills-interleave to combine the chosen skills.
