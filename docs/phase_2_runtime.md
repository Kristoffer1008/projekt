# Phase 2 Runtime Guide (Instructor Validation)

This guide validates Phase 2 only: simulation constants are moved to `config.yaml` and loaded consistently through `simulated_city.config.load_config()`.

## 1. What Was Created

### Notebooks/Scripts
- Updated notebook: `notebooks/agent_trigger.ipynb`

### Library modules added to `src/simulated_city/`
- No new module files added.
- Updated existing parser: `src/simulated_city/config.py` to support Phase 2 `simulation.*` keys.

### Configuration changes (`config.yaml` entries)
Added/confirmed `simulation:` section entries:
- `seed`
- `time_step_s`
- `simulated_hours_per_step`
- `publish_every_n_steps`
- `total_steps`
- `step_delay_s`
- `start_time`
- `population_size`
- `initial_infected`
- `infection_radius_m`
- `infection_probability`
- `recovery_days`
- `max_speed_m_per_s`
- `city_center.lat`
- `city_center.lon`
- `bounds.min_lat`
- `bounds.max_lat`
- `bounds.min_lon`
- `bounds.max_lon`

Also updated docs:
- `docs/config.md`

---

## 2. How to Run

### Workflow A: Run the Phase 2 Trigger notebook
1. Open `notebooks/agent_trigger.ipynb`.
2. Run Cell 1 (overview).
3. Run Cell 2 (load config + resolve simulation constants).
4. Run Cell 3 (initialize in-memory persons using config values).
5. Run Cell 4 (movement loop with reflection and config-driven cadence).
6. Run Cell 5 (config-aligned local schema preview).

Observe output:
- Cell 2 prints loaded config constants (seed, population, steps, bounds, health parameters).
- Cell 3 prints initialization counts from config (`population_size`, `initial_infected`).
- Cell 4 prints deterministic step lines (first three and last step) and completion message.
- Cell 5 prints one local dictionary with `lat/lon` and health parameters.

### Workflow B: Confirm config changes affect behavior
1. In `config.yaml`, change `simulation.population_size` from `300` to `100`.
2. Change `simulation.initial_infected` from `5` to `2`.
3. Save file.
4. Restart notebook kernel.
5. Re-run Cells 2 and 3.
6. Observe Cell 3 output changes to `Initialized 100 persons. infected=2, susceptible=98, ...`.

---

## 3. Expected Output

### Cell 2 — Load config constants
**Purpose:** Verify all simulation constants come from `config.yaml`.

**Exact expected output (with current defaults):**
- `Loaded config. seed=42, population=300, initial_infected=5, steps=1440, publish_every_n_steps=1`
- `Bounds lat=[55.62, 55.72] lon=[12.48, 12.66] center=(55.6761, 12.5683)`
- `Health params radius_m=2.0, infection_probability=0.5, recovery_days=10`

**If different:**
- Missing fields means notebook is not reading all Phase 2 constants.
- Different numeric values may be valid only if `config.yaml` was intentionally changed.

### Cell 3 — Initialize persons from config
**Purpose:** Verify population and initial infected counts are config-driven.

**Exact expected output (with current defaults):**
- `Initialized 300 persons. infected=5, susceptible=295, delta_scale=0.00001261`

**If different:**
- Count mismatch indicates config was changed or initialization logic regressed.
- `delta_scale` mismatch indicates time/speed constants changed.

### Cell 4 — Movement loop and reflection
**Purpose:** Verify deterministic movement using config bounds and timing settings.

**Exact expected output (with current defaults):**
- `Simulation start UTC: 2026-01-01T00:00:00+00:00`
- `step=0000 sample=person-000 lat=55.683937 lon=12.484495 susceptible=295 infected=5 recovered=0`
- `step=0001 sample=person-000 lat=55.683931 lon=12.484488 susceptible=295 infected=5 recovered=0`
- `step=0002 sample=person-000 lat=55.683926 lon=12.484481 susceptible=295 infected=5 recovered=0`
- `step=1439 sample=person-000 lat=55.675771 lon=12.485552 susceptible=295 infected=5 recovered=0`
- `Phase 2 simulation complete (local state only, no MQTT).`

**If different:**
- Step formatting changes may indicate notebook code changed.
- Coordinates outside configured bounds indicate reflection or bound loading issue.
- Count mismatch indicates initialization/state update issue.

### Cell 5 — Local schema preview
**Purpose:** Verify preview payload uses config-aligned keys and values.

**Exact expected output (with current defaults):**
```python
{'step': 1439, 'ts': '2026-01-15T23:45:00+00:00', 'person_id': 'person-000', 'lat': 55.675771, 'lon': 12.485552, 'health_status': 'infected', 'infection_radius_m': 2.0, 'infection_probability': 0.5, 'recovery_days': 10}
```

**If different:**
- Missing keys means schema is not phase-ready for later publish steps.
- Different values may be valid only when config values were intentionally modified.

---

## 4. MQTT Topics (if applicable)

Phase 2 does not use MQTT by design.

### Published topics
- None.

### Subscribed topics
- None.

### Message schemas
- No MQTT message transport in this phase.
- Cell 5 prints a local preview dictionary only.

---

## 5. Debugging Guidance

### Increase log detail
- Add temporary `print()` lines in Cell 2 for each resolved simulation variable.
- Add temporary boundary assertions in Cell 4 (for example: `assert min_lat <= sample.lat <= max_lat`).

### Common errors and fixes
- **`ValueError: Phase 2 requires a 'simulation' section in config.yaml`**
  - Fix: ensure `simulation:` exists in `config.yaml` with required keys.
- **`AttributeError` on simulation fields**
  - Fix: ensure latest `src/simulated_city/config.py` is loaded; restart kernel.
- **Unexpected counts/coordinates**
  - Fix: verify `population_size`, `initial_infected`, bounds, and seed in `config.yaml`.

### MQTT troubleshooting in this phase
- Not applicable. MQTT is intentionally not used in Phase 2.

---

## 6. Verification Commands

Run from project root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

Interpretation for this repository state:
- `verify_setup.py` should pass.
- `validate_structure.py` may show a non-blocking warning that agent notebook has no MQTT connect call; expected in Phase 2.
- `pytest` may fail in cloud MQTT credential/connectivity tests (`hivemq_cloud`) due environment authorization, not Phase 2 config logic.
