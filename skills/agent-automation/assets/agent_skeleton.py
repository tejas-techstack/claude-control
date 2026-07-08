#!/usr/bin/env python3
"""agent_skeleton: a safe, free-model agent loop you can copy and fill in.

Design goals baked in so the agent can't misbehave quietly:
  * dry-run by default (AGENT_DRY_RUN=1) — prints the action, doesn't take it
  * kill switch — a file (AGENT_STOP, default ./STOP) halts the loop between items
  * retries with exponential backoff on the model call
  * secrets from env only; a fail-loud validator so bad model output never acts
  * timestamped logging to stdout + a logfile

Model backend is pluggable via call_model(); the default targets an OpenAI-compatible
endpoint, which is what most FREE options expose (Ollama local, Groq/OpenRouter free
tiers). Set the three env vars and go. Stdlib only.

  MODEL_BASE_URL   e.g. http://localhost:11434/v1  (Ollama, fully free/local)
  MODEL_NAME       e.g. llama3.1  /  qwen2.5  /  a free hosted model id
  MODEL_API_KEY    "ollama" locally, or your free-tier key (never hardcode it)
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

DRY_RUN = os.environ.get("AGENT_DRY_RUN", "1") != "0"        # safe by default
STOP_FILE = os.environ.get("AGENT_STOP", "STOP")
LOG_FILE = os.environ.get("AGENT_LOG", "agent.log")
BASE = os.environ.get("MODEL_BASE_URL", "http://localhost:11434/v1").rstrip("/")
MODEL = os.environ.get("MODEL_NAME", "llama3.1")
KEY = os.environ.get("MODEL_API_KEY", "ollama")


def log(msg):
    line = "%s  %s" % (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg)
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def stop_requested():
    if os.path.exists(STOP_FILE):
        log("kill switch %s present — stopping." % STOP_FILE)
        return True
    return False


def call_model(prompt, system="You are a careful assistant.", retries=4):
    """OpenAI-compatible /chat/completions call with backoff. Returns the text."""
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}], "temperature": 0}).encode()
    delay = 1.0
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(BASE + "/chat/completions", data=body,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + KEY})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
            return data["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, KeyError, ValueError) as e:
            log("model call failed (attempt %d/%d): %s" % (attempt, retries, e))
            if attempt == retries:
                raise
            time.sleep(delay)
            delay *= 2


# ---- fill these in for your task -------------------------------------------

def fetch_inputs():
    """Return the work items. Replace with your source (files, API, queue, DB)."""
    return [{"id": 1, "text": "example item to process"}]


def build_prompt(item):
    """Turn one item into a tight, single-purpose prompt (see /prompt-suggest)."""
    return "Summarize this in one sentence:\n\n" + item["text"]


def validate(output, item):
    """Fail LOUD on bad output so the agent never acts on garbage. Raise to reject."""
    if not output or len(output) > 2000:
        raise ValueError("output empty or too long")
    return output


def take_action(item, result):
    """The side effect. Guarded by DRY_RUN. Replace with your real action."""
    if DRY_RUN:
        log("DRY-RUN would act on item %s -> %r" % (item["id"], result[:120]))
        return
    log("ACTING on item %s" % item["id"])
    # ... real side effect here (write file, post comment, send message) ...


# ---- the loop --------------------------------------------------------------

def main():
    log("start  dry_run=%s model=%s base=%s" % (DRY_RUN, MODEL, BASE))
    items = fetch_inputs()
    ok = fail = 0
    for item in items:
        if stop_requested():
            break
        try:
            result = validate(call_model(build_prompt(item)), item)
            take_action(item, result)
            ok += 1
        except Exception as e:                        # fail loud, keep going
            fail += 1
            log("ERROR on item %s: %s" % (item.get("id"), e))
    log("done  ok=%d fail=%d  (dry_run=%s)" % (ok, fail, DRY_RUN))
    sys.exit(1 if fail and not ok else 0)


if __name__ == "__main__":
    main()
