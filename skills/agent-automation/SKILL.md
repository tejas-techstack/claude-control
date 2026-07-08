---
name: agent-automation
description: Assess whether a project can benefit from agentic automation, and if the user accepts, design, build, and test a complete agent system using only free-to-use models and free orchestration — zero recurring cost. Use whenever the user mentions agents, automating a workflow with AI, "make this run itself", scheduled AI jobs, or a project has an obvious repetitive AI-shaped loop.
---

# Agent Automation (zero-cost)

Suggest first, build on acceptance, prove it works. Read `../_shared/GUARDRAILS.md` first — the free-only rule is the whole point here.

## Step 1 — assess and propose
Identify the loop worth automating (triage issues, summarize inputs, monitor + report, transform data, draft responses). Propose it with an honest note: what quality to expect from free models, and what stays manual. Get an explicit yes before building.

## Step 2 — pick free components (verify current free status before recommending — offerings change)
- **Models, local (truly free, private):** Ollama or llama.cpp running Llama/Qwen/Mistral-class open-weight models. Default choice when the machine can run them.
- **Models, hosted free tiers (no card):** check current terms of e.g. Google AI Studio/Gemini free tier, Groq free tier, OpenRouter free models, Hugging Face Inference free tier. State rate limits honestly.
- **Orchestration (free):** plain Python/cron; GitHub Actions on schedule (free quota); n8n self-hosted; Node-RED. Prefer the simplest that works — usually a Python script + cron/Actions.
- **Never** wire in anything that needs a subscription or card. If quality demands a paid model, say so and stop at the design.

## Step 3 — build small and safe
One agent, one loop: fetch inputs -> model call with a tight prompt (use template 23 in /prompt-suggest library) -> validated output -> action or report. Include: retries with backoff, a dry-run mode, logging, and a kill switch (a file or env var that halts it). Secrets via env vars only.

## Step 4 — test before handover
Run the loop on 3+ real samples and show outputs. Test the failure paths (model down, bad output) — the agent must fail loudly, not silently. Deliver a RUNBOOK.md: how to run, schedule, monitor, and stop it.

## Chaining
- Input: a repetitive workflow; scope it with /cross-check. Output: working agent + RUNBOOK.md; run it contained via /isolate, find components via /free-alternatives.
