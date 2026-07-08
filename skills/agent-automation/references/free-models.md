# Free models & orchestration for agents

**Always verify the current free terms before recommending — tiers, rate limits, and card requirements change often.** State the limit you find out loud. If quality genuinely needs a paid model, say so and stop at the design rather than quietly wiring in a bill.

## Models — local (truly free, private, no card, no cap)

The default. If the machine can run it, prefer it.

- **Ollama** (`ollama.com`) — one-line install, `ollama pull llama3.1` / `qwen2.5` / `mistral` / `gemma2`, serves an **OpenAI-compatible** API at `http://localhost:11434/v1`. Works with `assets/agent_skeleton.py` unchanged (`MODEL_BASE_URL=http://localhost:11434/v1`, `MODEL_API_KEY=ollama`).
- **llama.cpp** — lower-level, great on modest hardware; also exposes an OpenAI-compatible server.
- Sizing: 7–8B models run on ~8GB RAM (CPU ok, slow); quantized (Q4) fits smaller. Set expectations: local small models are fine for summarize/classify/extract/draft, weaker at long reasoning.

## Models — hosted free tiers (no card, but rate-limited)

Use when the machine can't run a model, or you need more quality than a local 7B. Verify terms first; all expose OpenAI-compatible endpoints, so only the three env vars change.

- **Google AI Studio / Gemini** free tier — generous, good quality; check current RPM/RPD limits.
- **Groq** free tier — very fast inference of open models; check limits.
- **OpenRouter** — has a set of `:free` model ids; check which are currently free and their caps.
- **Hugging Face Inference** free tier — many open models; rate-limited.

Honesty rule: name the rate limit and what happens when you hit it (the skeleton retries with backoff, then fails loud).

## Orchestration — free

Prefer the simplest that works. Usually a script + a scheduler.

| Need | Free tool |
|---|---|
| Run on a schedule | cron (Linux/macOS) · Task Scheduler (Windows) · GitHub Actions `schedule:` (free quota) |
| Event/webhook driven | GitHub Actions on events · a tiny `http.server` · n8n (self-host) |
| Multi-service visual flows | n8n (self-host) · Node-RED |
| Just glue | a plain Python script (the skeleton) |

Don't reach for a framework when 60 lines + cron do it. Add LangChain/CrewAI/etc. only if the task genuinely needs multi-tool planning — and even then, check it's free and worth the dependency.

## Safety rails every agent gets (already in the skeleton)

- **Dry-run by default** (`AGENT_DRY_RUN=1`) — prove the outputs before it's allowed to act.
- **Kill switch** — a `STOP` file halts the loop between items; document where it is.
- **Retries with backoff**, **fail-loud validation** (never act on malformed output), **timestamped logs**, **secrets from env only**.
- Test on 3+ real samples and simulate a failure (model down, bad output) before handover.
