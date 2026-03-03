# Phase 6 Runtime Verification

This document captures how to validate Phase 6 (Control + Response agents) in the distributed notebook architecture.

## Scope

Phase 6 adds:

- `notebooks/agent_control.ipynb`
- `notebooks/agent_response.ipynb`
- `src/simulated_city/epidemic.py`

Validation goals:

1. Control receives Trigger + Observer messages and publishes health updates.
2. Response receives Observer + Control messages and publishes one metrics payload per step.
3. Verification scripts and tests pass.

## Manual notebook run order

Use separate notebook kernels/tabs:

1. Run `notebooks/agent_observer.ipynb` Cells 1–4.
2. Run `notebooks/agent_control.ipynb` Cells 1–4.
3. Run `notebooks/agent_response.ipynb` Cells 1–4.
4. Run `notebooks/dashboard.ipynb` Cells 1–4.
5. Run `notebooks/agent_trigger.ipynb` Cells 1–4.
6. After activity, run summary/cleanup cells:
   - Observer Cell 5
   - Control Cell 5
   - Response Cell 5
   - Dashboard Cell 5

Expected signs:

- Control prints subscriptions to Trigger + Observer topics.
- Control summary shows non-zero `health_updates_published` after trigger traffic.
- Response prints subscriptions to Observer + Control topics.
- Response summary shows non-zero `metrics_published` and progressing `last_step_seen`.
- Dashboard continues to render map markers and city counters (read-only).

## Command-line validation

Run from repository root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

## Notes

- If notebook imports do not reflect new `src/simulated_city` changes, restart the affected kernel and re-run setup cells.
- If an external MQTT profile is unavailable, switch to a reachable profile in `config.yaml` before rerunning manual checks.
