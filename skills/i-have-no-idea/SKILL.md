---
name: i-have-no-idea
description: An interactive discovery session for when the user does not know what they want — they found an interesting repo but have no idea how to use/apply it, or they know WHAT they want but not HOW, or know HOW but not WHY. Use whenever the user says "I have no idea", "not sure what to do with this", "found this repo, now what", "where do I even start", or gives an aimless open-ended message about a project.
---

# I Have No Idea (discovery mode)

The user is lost; be a patient, opinionated guide. Read `../_shared/GUARDRAILS.md` first. `references/discovery.md` expands each branch below into ready phrasings, the proposal scripts, and the tone rules — open it for the full flow.

## Step 1 — locate the confusion (ask exactly one question)
"Which is closest? (a) I have a THING (repo/tool/dataset) and no idea what to do with it. (b) I have a GOAL and no idea how to reach it. (c) I know how, but not whether/why it is worth doing. (d) Genuinely none — just exploring."

## Step 2 — run the matching loop (max 2 questions per turn, always offer concrete options)
- **(a) Thing, no goal**: quickly understand the thing (repo_map.py / README, or /humanize for depth). Then PROPOSE, never interrogate: "Here are 4 things people like you could do with this — learn from it, use it as a library for X, build Y on top, or harvest just component Z." Ask which sparks anything; iterate on the spark.
- **(b) Goal, no how**: restate the goal sharply, then present 2-3 routes with effort estimates and the first concrete step of each. Recommend one and say why.
- **(c) How, no why**: play honest devil advocate — who benefits, what already exists (/github-explore), what it costs to build vs adopt. End with a clear "worth it / not worth it because...".
- **(d) Exploring**: ask about their skills and interests once, then suggest 3 project directions matched to them, each with a 30-minute first experiment.

## Step 3 — land the plane
Every session MUST end with: a one-paragraph statement of what they are actually trying to achieve (their words, sharpened), the next 1-3 concrete actions, and which skills to invoke for each (e.g., /cross-check before building, /research before deciding).

## Chaining
- Input: confusion. Output: a direction; feeds /cross-check, /research, /prompt-suggest.
