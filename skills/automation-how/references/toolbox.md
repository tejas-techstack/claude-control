# Automation toolbox — pick the simplest free machine

Match the chore to the lightest tool that does it. Recommend in this order; climb only when the lower tier can't. Verify a service's *current* free tier before recommending — tiers change. Copy-paste templates are in `assets/`.

## The ladder

1. **Script + scheduler** — Python/bash + cron (Linux/macOS) or Task Scheduler (Windows). Zero services, fully private, no account. The right answer ~70% of the time. On Linux, systemd timers are the sturdier cron (logs, retries, dependencies).
2. **GitHub Actions** on `schedule:` / events — free quota, no server, ideal when the data already lives in a repo or the trigger is a repo event.
3. **n8n (self-hosted)** — visual node editor, hundreds of integrations; the free answer to Zapier for chaining 3+ SaaS services.
4. **Node-RED** — event/IoT-flavored flows, very light, self-hosted.
5. **OS-native** — systemd path/timer units, `launchd` (macOS), folder-watchers, udev.

Avoid: anything needing a paid plan or card for the trigger/action you need; privacy-hostile services.

## Choose by trigger

| Trigger | Reach for |
|---|---|
| A time / schedule | cron · systemd timer · Actions `schedule:` |
| A file appears/changes | systemd `.path` unit · `watchdog` (Python) · Node-RED |
| A webhook / HTTP call | a tiny `http.server` · Actions `repository_dispatch` · n8n |
| A repo event (push/PR/issue) | GitHub Actions |
| An email arrives | n8n IMAP node · a fetch-mail script on a timer |
| 3+ SaaS hops | n8n self-hosted |

## Build it properly (whatever the tier)

- **Concrete artifacts**, not instructions: the actual script / workflow YAML / n8n flow JSON.
- **Secrets** via env vars or the platform's secret store — never in the file.
- **Dry-run flag** and **idempotency** (safe to run twice).
- **Logging** with timestamps; know where the logs land.
- **A kill switch** and a documented way to disable it.
- Test the happy path live, and simulate one failure (source down) to show behavior.

## cron quick reference

```
┌ minute (0-59)
│ ┌ hour (0-23)
│ │ ┌ day of month (1-31)
│ │ │ ┌ month (1-12)
│ │ │ │ ┌ day of week (0-6, 0=Sun)
* * * * *  command
```

`*/15 * * * *` every 15 min · `0 9 * * 1-5` weekdays 9am · `0 0 * * 0` Sundays midnight. Use absolute paths in cron (its env is minimal); redirect output: `>> job.log 2>&1`. Test the schedule at crontab.guru before trusting it.

## Deliver a mini-runbook

Install/enable, how to verify it ran, where the logs are, and how to STOP it. (For AI-in-the-loop automations, hand off to `/agent-automation`; to contain a risky one, `/isolate`.)
