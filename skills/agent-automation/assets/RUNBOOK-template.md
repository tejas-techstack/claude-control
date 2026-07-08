# RUNBOOK: <agent name>

What it does, in one sentence: <…>

## What it touches

- Inputs: <source>
- Action / side effect: <what it changes in the world>
- Model: <local Ollama model / hosted free tier> — cost: free (<rate limit if hosted>)

## Run it

```bash
# 1. configure (secrets via env only — never commit them)
export MODEL_BASE_URL=http://localhost:11434/v1
export MODEL_NAME=llama3.1
export MODEL_API_KEY=ollama

# 2. dry-run first (default) — prints intended actions, changes nothing
python3 agent.py

# 3. go live only after the dry-run output looks right
AGENT_DRY_RUN=0 python3 agent.py
```

## Schedule it (pick one)

```bash
# cron — every day at 09:00
0 9 * * *  cd /path/to/agent && AGENT_DRY_RUN=0 /usr/bin/python3 agent.py >> cron.log 2>&1
```

Or GitHub Actions `on: schedule:` (free quota) — see `/automation-how` for the workflow file.

## Monitor it

- Logs: `agent.log` (timestamped) and stdout/cron.log.
- Success signal: <what a healthy run prints / where results land>.
- It fails LOUD: a bad model response or downstream error is logged as ERROR and the run exits non-zero.

## Stop it

- **Now**: `touch STOP` — the loop halts before the next item.
- **Permanently**: remove the cron line / disable the workflow, then delete `STOP`.

## When it breaks

| Symptom | Likely cause | Fix |
|---|---|---|
| all items ERROR | model endpoint down / wrong `MODEL_BASE_URL` | check `curl $MODEL_BASE_URL/models`; restart Ollama |
| rate-limit errors | hosted free-tier cap hit | slow the schedule, or switch to local Ollama |
| acts wrongly | prompt or validator too loose | tighten `build_prompt` / `validate`, re-run dry-run on real samples |
