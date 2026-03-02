# Phase 1 Runtime Guide

## 1. What Was Created

### Notebooks/Scripts
- Created notebook: `notebooks/agent_trigger.ipynb`
- Updated documentation: `docs/exercises.md` (new Phase 1 section)

### Library modules added to `src/simulated_city/`
- None in Phase 1.

### Configuration changes (`config.yaml`)
- None required for Phase 1 implementation.
- Phase 1 reads existing configuration via `simulated_city.config.load_config()` and uses available simulation defaults.

---

## 2. How to Run

### Workflow A: Run the Trigger agent notebook (Phase 1 only)
1. Open `notebooks/agent_trigger.ipynb`.
2. Run Cell 1 (markdown overview) to confirm scope.
3. Run Cell 2 (imports + config load).
4. Run Cell 3 (initialize persons).
5. Run Cell 4 (movement loop).
6. Run Cell 5 (local schema preview).

Expected observation flow:
- After Cell 2: config/seed confirmation is printed.
- After Cell 3: initialization summary is printed.
- After Cell 4: 10 step lines are printed with counts and a sample person position.
- After Cell 5: one dictionary-like message preview is printed.

### Workflow B: Repeatability check (determinism)
1. Restart notebook kernel.
2. Re-run Cells 2–5.
3. Compare the printed `step=00...step=09` sample positions against previous run.

Expected result:
- With the same config seed, outputs should repeat exactly.
- If outputs differ, check `simulation.seed` and random-seed loading behavior.

---

## 3. Expected Output

### Cell 2 — Load config
**Purpose:** Confirm config is loaded and deterministic random settings are active.

**Expected output format:**
- `Loaded config. Deterministic seed=<number>, step_delay_s=<number>`

**Success criteria:**
- Message appears once.
- `seed` is numeric.

**If different:**
- If import error appears, environment is not configured correctly.
- If config loading fails, check `config.yaml` path and syntax.

### Cell 3 — Initialize local person states
**Purpose:** Build initial local state for Trigger agent.

**Expected output format:**
- `Initialized 12 persons. infected=1, susceptible=11`

**Success criteria:**
- Exactly 12 persons are initialized.
- One infected person and remaining susceptible.

**If different:**
- Different counts indicate modified initialization logic or edited population size.

### Cell 4 — Run movement loop with edge reflection
**Purpose:** Simulate local movement for 10 steps and verify boundary reflection.

**Expected output format:**
- First line: `Simulation start UTC: <ISO-8601 timestamp>`
- Ten lines with this shape:
  - `step=00 sample=person-000 x=<float> y=<float> susceptible=11 infected=1 recovered=0`
  - ... up to `step=09 ...`
- Final line:
  - `Phase 1 simulation complete (local state only, no MQTT).`

**Success criteria:**
- Steps run from `00` to `09`.
- Health counts remain internally consistent and sum to 12 each step.
- Sample `x`/`y` remain within boundaries (normalized box or configured location extent).

**If different:**
- Missing step lines: loop did not execute fully.
- Positions outside bounds: reflection function is incorrect.
- Count mismatch: state update logic is broken.

### Cell 5 — Local publishing-ready schema preview
**Purpose:** Show minimal local message structure for next phases without sending MQTT.

**Expected output format:**
- A dictionary with keys:
  - `step`, `ts`, `person_id`, `x`, `y`, `health_status`

Example shape:
```python
{
  'step': 9,
  'ts': '2026-...+00:00',
  'person_id': 'person-000',
  'x': 0.123456,
  'y': 0.654321,
  'health_status': 'infected'
}
```

**Success criteria:**
- All keys are present.
- `health_status` is a valid local state string.

**If different:**
- Missing keys means the schema is not ready for Phase 3 publishing.

---

## 4. MQTT Topics (if applicable)

Phase 1 does not use MQTT by design.

### Published topics
- None.

### Subscribed topics
- None.

### Message schemas used over MQTT
- None in this phase.
- Only local in-memory preview schema is shown in notebook Cell 5.

---

## 5. Debugging Guidance

### Increase runtime visibility
- Re-run Cell 4 after adding temporary `print()` statements for `dx`/`dy` to inspect reflection behavior.
- Restart kernel before each test pass to avoid stale state.

### Common errors and fixes
- **`ModuleNotFoundError: simulated_city`**
  - Fix: activate the project environment and install editable dependencies.
- **Config load errors**
  - Fix: validate `config.yaml` syntax and run from repository workspace so parent lookup works.
- **Non-deterministic output**
  - Fix: confirm `simulation.seed` is set or fallback seed remains unchanged.

### How to verify local state flow
- Confirm Cell 3 initializes expected counts.
- Confirm Cell 4 prints exactly 10 ordered step records.
- Confirm Cell 5 contains all preview-schema keys.

---

## 6. Verification Commands

Run these commands from project root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

Interpretation:
- `verify_setup.py`: confirms dependencies/environment setup.
- `validate_structure.py`: confirms repository structure rules.
- `pytest`: confirms existing automated tests still pass.
