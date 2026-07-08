---
name: agent-automation
description: Assess whether a project can benefit from agentic automation, and if the user accepts, design, build, and test a complete agent system using only free-to-use models and free orchestration — zero recurring cost. Use whenever the user mentions agents, automating a workflow with AI, "make this run itself", scheduled AI jobs, or a project has an obvious repetitive AI-shaped loop.
---

# Agent Automation (zero-cost)

Suggest first, build on acceptance, prove it works. Read `../_shared/GUARDRAILS.md` first — the free-only rule is the whole point here.

## Step 1 — assess and propose
Identify the loop worth automating (triage issues, summarize inputs, monitor + report, transform data, draft responses). Propose it with an honest note: what quality to expect from free models, and what stays manual. Get an explicit yes before building.

## Step 2 — pick free components (verify current free status before recommending — offerings change)
`references/free-models.md` is the current menu: local Ollama/llama.cpp (default, no card, no cap), hosted free tiers (Gemini/Groq/OpenRouter/HF — state rate limits), and free orchestration (cron, GitHub Actions, n8n). All expose OpenAI-compatible endpoints, so only three env vars change. **Never** wire in anything needing a subscription or card; if quality demands a paid model, say so and stop at the design.

## Step 3 — build small and safe
Start from `assets/agent_skeleton.py` — a runnable loop that already bakes in the safety rails: dry-run by default, a `STOP`-file kill switch, retries with backoff, fail-loud output validation, timestamped logging, and secrets-from-env. Fill in `fetch_inputs` / `build_prompt` (tight, single-purpose — see /prompt-suggest) / `validate` / `take_action`. One agent, one loop.

## Step 4 — test before handover
Run the loop on 3+ real samples in dry-run and show outputs. Test the failure paths (model down, bad output) — the agent must fail loudly, not silently. Deliver a filled `assets/RUNBOOK-template.md` as RUNBOOK.md: how to run, schedule, monitor, and stop it.

## Chaining
- Input: a repetitive workflow; scope it with /cross-check. Output: working agent + RUNBOOK.md; run it contained via /isolate, find components via /free-alternatives.
