# Phase 4 Runtime Guide (Instructor Validation)

This guide validates Phase 4 only: a second agent notebook (`agent_observer`) subscribes to Trigger person-state messages and publishes exposure candidates + city snapshots.

## 1. What Was Created

### Notebooks/Scripts
- Created notebook: `notebooks/agent_observer.ipynb`
- Updated notebook: `notebooks/agent_trigger.ipynb` (unique MQTT client ID suffix for concurrent run stability)

### Library modules added to `src/simulated_city/`
- No new module files created.
- Updated existing helper behavior in `src/simulated_city/mqtt.py`:
  - `publish_json_checked(...)` now retries transient disconnected publish windows.

### Configuration changes (`config.yaml` entries)
- No new config keys required for Phase 4.
- Phase 4 reuses existing `mqtt.*` and `simulation.*` values.

### Documentation updates
- `docs/mqtt.md` (observer topic contracts + schemas)
- `docs/exercises.md` (Phase 4 section + multi-notebook run steps)
- `docs/phase_4_runtime.md` (this file)

---

## 2. How to Run

### Workflow A: Start Observer first
1. Open `notebooks/agent_observer.ipynb`.
2. Run Cell 1 (overview).
3. Run Cell 2 (config + topic setup).
4. Run Cell 3 (buffers + processing logic).
5. Run Cell 4 (connect + subscribe callback).

Expected observer state after Cell 4:
- Connected to broker
- Subscribed to `simulated-city/pandemic/trigger/person_state`
- Waiting for Trigger data

### Workflow B: Start Trigger publisher
1. Open `notebooks/agent_trigger.ipynb`.
2. Run Cells 1–3.
3. Run Cell 4 to publish Trigger person-state stream.
4. Run Cell 5 to print final payload preview and disconnect.

### Workflow C: Read Observer results
1. Return to `notebooks/agent_observer.ipynb`.
2. Run Cell 5 (summary + disconnect).

Expected change in observer summary:
- `steps_processed` should be greater than `0`.
- `city_snapshots_published` should be greater than `0`.
- `exposure_events_published` may be `0` if no infected/susceptible pairs are within configured radius.

---

## 3. Expected Output

### Observer Cell 2 — Config + contracts
**Purpose:** Verify observer parameters and topic contracts are loaded from config.

**Exact expected output (current defaults):**
- `Observer config loaded. population_size=300, infection_radius_m=2.0`
- `Step completion threshold: 270/300 persons`
- `Subscribe topic: simulated-city/pandemic/trigger/person_state`
- `Publish topics: simulated-city/pandemic/observer/exposure_event, simulated-city/pandemic/observer/city_snapshot`

### Observer Cell 4 — Connect + subscribe
**Purpose:** Verify observer is online before Trigger starts.

**Exact expected output:**
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Subscribed to simulated-city/pandemic/trigger/person_state`
- `Observer is now listening. Run Trigger notebook publish cell to feed this agent.`

### Trigger Cell 4 — Publish stream (integration run)
**Purpose:** Send Trigger stream while observer is subscribed.

**Expected key lines:**
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Simulation start UTC: 2026-01-01T00:00:00+00:00`
- `step=0000 ...`
- `step=0001 ...`
- `step=0002 ...`
- `step=1439 ...`
- `Phase 3 publish complete. published_messages=432000 topic=simulated-city/pandemic/trigger/person_state`

### Observer Cell 5 — Summary + disconnect
**Purpose:** Confirm observer processed step batches and published observer outputs.

**Exact observed output from validation run:**
- `Observer summary: steps_processed=106, exposure_events_published=0, city_snapshots_published=106, pending_steps=94`
- `Disconnected from MQTT broker.`

Interpretation:
- `steps_processed > 0` and `city_snapshots_published > 0` confirm working distributed flow.
- `exposure_events_published=0` is valid when no pair distance is below `infection_radius_m` in processed batches.

---

## 4. MQTT Topics

### Trigger topic (input to Observer)
- Topic: `simulated-city/pandemic/trigger/person_state`
- Publisher: `notebooks/agent_trigger.ipynb`
- Subscriber: `notebooks/agent_observer.ipynb`
- Payload schema:
```json
{
  "step": 0,
  "ts": "2026-01-01T00:00:00+00:00",
  "person_id": "person-000",
  "lat": 55.683937,
  "lon": 12.484495,
  "health_status": "infected"
}
```

### Observer exposure output
- Topic: `simulated-city/pandemic/observer/exposure_event`
- Publisher: `notebooks/agent_observer.ipynb`
- Payload schema:
```json
{
  "step": 0,
  "ts": "2026-01-01T00:00:00+00:00",
  "source_id": "person-000",
  "target_id": "person-111",
  "distance_m": 1.732,
  "within_radius": true
}
```

### Observer snapshot output
- Topic: `simulated-city/pandemic/observer/city_snapshot`
- Publisher: `notebooks/agent_observer.ipynb`
- Payload schema:
```json
{
  "step": 0,
  "ts": "2026-01-01T00:00:00+00:00",
  "population": 300,
  "infected_count": 5,
  "susceptible_count": 295,
  "recovered_count": 0,
  "active_exposures": 0
}
```

---

## 5. Debugging Guidance

### Data buffering and ordering strategy
- Observer buffers Trigger messages in `step_people[step][person_id]`.
- A step is processed when either:
  - full batch arrives (`population_size` persons), or
  - at least `90%` batch arrives and a newer step is observed.
- This avoids deadlock from minor packet loss/out-of-order delivery.

### Common errors and fixes
- **Trigger and Observer disconnect each other immediately**
  - Cause: same MQTT client ID.
  - Fix: use unique suffixes (`trigger`, `observer`) in `connect_mqtt(..., client_id_suffix=...)`.
- **`MQTT publish failed (rc=4)` during burst publish**
  - Cause: transient disconnect under load.
  - Fix: helper retries are built in; if persistent, reduce message volume via `publish_every_n_steps`.
- **Observer summary shows zero processed steps**
  - Check observer Cell 4 ran before Trigger Cell 4.
  - Verify both notebooks target same `mqtt.base_topic` and broker profile.

### How to verify MQTT flow
- Use terminal monitor:
  ```bash
  mosquitto_sub -h 127.0.0.1 -v -t "simulated-city/pandemic/observer/#"
  ```
- While Trigger and Observer run, confirm `observer/city_snapshot` messages appear.

---

## 6. Verification Commands

Run from project root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

Expected status for current repository:
- `verify_setup.py` passes.
- `validate_structure.py` passes.
- `pytest` passes.
