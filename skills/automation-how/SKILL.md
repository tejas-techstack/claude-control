---
name: automation-how
description: Recommend and build free workflow automations that chain tools together — schedulers, watchers, webhooks, pipelines — using self-hosted or genuinely free services. Use whenever the user asks "how do I automate X", wants to connect tool A to tool B, mentions Zapier/IFTTT/n8n or cron, or describes a manual multi-step routine.
---

# Automation How (free workflow automation)

Pick the simplest free machine that does the chore. Read `../_shared/GUARDRAILS.md` first.

## The free toolbox (recommend in this order)
1. **A script + scheduler** — Python/bash + cron (Linux/macOS) or Task Scheduler (Windows). Zero services, fully private. Right answer ~70% of the time.
2. **GitHub Actions on `schedule:`/webhooks** — free quota, no server, great when the data already lives in a repo.
3. **n8n (self-hosted)** — visual node editor, hundreds of integrations, free to self-host; the free answer to Zapier for multi-service chains.
4. **Node-RED** — event/IoT-ish flows, very light, self-hosted.
5. OS-native: udev/systemd timers, launchd, folder-watchers.
Avoid: anything requiring a paid plan or card for the needed trigger/action; privacy-hostile services. Verify a services CURRENT free tier before recommending — tiers change. Full tier-by-trigger matrix and a cron cheatsheet are in `references/toolbox.md`.

## Workflow
1. Get the chain as "WHEN trigger -> DO steps -> RESULT where". Identify trigger type (time, file, webhook, email, repo event).
2. Match to the toolbox: single machine + time trigger -> option 1; repo events -> option 2; 3+ SaaS hops -> option 3. Say why in one line. Reference `references/toolbox.md` for the trigger→tool table.
3. Build it concretely: the actual script/workflow file/n8n flow JSON — not pseudo-instructions. Start from `assets/gh-actions-schedule.yml` or `assets/systemd-timer.md` when they fit. Env vars for secrets; a dry-run flag; logging with timestamps.
4. Test the happy path live if possible, and simulate one failure (source down) to show the behavior.
5. Deliver a mini-runbook: install/enable, verify it ran, logs location, and how to STOP it.

## Chaining
- Input: a routine (often found by /improvements). Output: running automation + runbook; add AI steps via /agent-automation, contain risky ones via /isolate.
