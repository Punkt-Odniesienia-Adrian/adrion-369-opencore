# ADRION 369 — Open Core

Transparency, causality, and consistency checks for autonomous AI agent
decisions — three reference modules from the ADRION 369 ethics-governance
layer, released as MIT-licensed open source.

## What this is

Autonomous AI agents increasingly make decisions that matter — approvals,
denials, recommendations — with no inspectable record of *why*. This
package provides three independent, composable checks you can drop into
any agent pipeline:

- **`TransparencyLog`** — an append-only, hash-chained audit log. Every
  decision is cryptographically linked to the one before it, so tampering
  with history is detectable, not just discouraged.
- **`CausalityTracker`** — records the reasoning steps behind a decision,
  so "why did the agent do X" has a concrete answer instead of a shrug.
- **`UnityChecker`** — flags when a new decision contradicts a prior
  decision on a comparable input, before the contradiction reaches a user.

## Install

```bash
pip install adrion-opencore
```

(PyPI publication pending — for now, install directly from this repo:
`pip install git+https://github.com/Punkt-Odniesienia-Adrian/adrion-369-opencore`)

## Quick example

```python
from adrion_opencore import TransparencyLog, CausalityTracker, UnityChecker

log = TransparencyLog()
tracker = CausalityTracker()
unity = UnityChecker()

trace = tracker.start_trace("txn-42", "approve_transaction")
trace.add_step("check_amount_threshold", {"amount": 100}, "under_threshold")

result = unity.check(input_signature="user:u1|type:withdrawal", proposed_decision="approve")
if result.consistent:
    log.record(actor="agent-1", action="approve_transaction", payload={"amount": 100})
    unity.record("user:u1|type:withdrawal", "approve")

assert log.verify_chain()
```

## What's in the full (enterprise) version

This open-core package covers 3 of the 9 guardian checks in the full
ADRION 369 system. The remaining 6 — including the two with **veto power**
(privacy, nonmaleficence) — plus the full 162-dimensional decision space,
formal mathematical verification, and compliance tooling for the EU AI
Act, are part of the enterprise offering. Full technical review available
under a confidentiality agreement — contact below.

## Status

Early stage, actively developed by a solo founder. Test suite: 11/11
passing (`pytest tests/`). Not yet published to PyPI.

## License

MIT — see `LICENSE`.

## Contact

Adrian Halicki — punktodniesienia.adrian@gmail.com
