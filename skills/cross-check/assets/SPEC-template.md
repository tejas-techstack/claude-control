# SPEC: <project / feature name>

> Status: DRAFT — building starts only after the user replies **APPROVE**.
> Author: <who> · Date: <YYYY-MM-DD> · Cross-check depth: deep | shallow

## Goal

One or two sentences: the problem this solves and the end state. If you can't state it in two sentences, the scope is still too fuzzy.

## Users / stakeholders

- Primary user: <who, and what they're trying to accomplish>
- Secondary / affected: <ops, other services, downstream consumers>

## Requirements (MoSCoW)

| Priority | Requirement | Acceptance signal |
|---|---|---|
| Must | … | … |
| Must | … | … |
| Should | … | … |
| Could | … | … |
| Won't (this version) | … | — |

## Non-goals

Explicitly out of scope, so nobody expects them later:

- …

## Constraints

- Stack / runtime: …
- Environment: …
- Budget: free unless noted — <any paid service?>
- Security / privacy: <PII, secrets, auth, compliance>
- Dependencies / licenses: …
- Deadline / "good enough" bar: …

## Interfaces & data

- Inputs: <shape, source, trust level, volume>
- Outputs: <shape, consumer>
- Interface: <CLI / API / UI / job>
- Persistence: <what, where>
- Scale expected: <realistic numbers>

## Edge cases & failure behavior

- Worst inputs: …
- On failure: <crash / retry / degrade / alert>; idempotent on retry? <y/n>
- Concurrency: …
- Migration / backward-compat: …

## Acceptance criteria (objective, checkable)

1. …
2. …
3. …

## How the user verifies

<the demo / command / check the user runs to confirm it's done>

## Open questions

- [ ] …

---
**Reply `APPROVE` to lock this spec.** Changes after approval re-open the spec (note them in a changelog line below).

_Changelog:_
- <date> — initial draft
