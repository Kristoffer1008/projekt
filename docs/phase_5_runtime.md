# Phase 5 Runtime Guide (Instructor Validation)

This guide validates Phase 5 only: a read-only dashboard notebook subscribes to raw MQTT simulation topics and renders live map overlays with anymap-ts.

## 1. What Was Created

### Notebooks/Scripts
- Created notebook: `notebooks/dashboard.ipynb`

### Library modules added to `src/simulated_city/`
- None in Phase 5.

### Configuration changes (`config.yaml` entries)
- No new keys added in Phase 5.
- Dashboard uses existing config values:
  - `mqtt.base_topic`
  - `mqtt.profiles.*` active profile
  - `simulation.city_center.lat`
  - `simulation.city_center.lon`

### Documentation updates
- Updated: `docs/maplibre_anymap.md`
- Updated: `docs/exercises.md`
- Added: `docs/phase_5_runtime.md`

---

## 2. How to Run

### Workflow A: Start Observer subscriber
1. Open `notebooks/agent_observer.ipynb`.
2. Run Cell 1 (overview).
3. Run Cell 2 (config + topic contracts).
4. Run Cell 3 (distance/processing logic).
5. Run Cell 4 (connect + subscribe).

Observe output:
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Subscribed to simulated-city/pandemic/trigger/person_state`

### Workflow B: Start Dashboard (read-only)
1. Open `notebooks/dashboard.ipynb`.
2. Run Cell 1 (overview).
3. Run Cell 2 (config + topic setup).
4. Run Cell 3 (create anymap-ts map).
5. Run Cell 4 (connect + subscribe to raw topics).

Observe output:
- `Dashboard config loaded. center=(12.5683, 55.6761), subscribe=simulated-city/pandemic/#`
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Subscribed to simulated-city/pandemic/#`

### Workflow C: Start Trigger publisher
1. Open `notebooks/agent_trigger.ipynb`.
2. Run Cells 1–3 (setup + initialize).
3. Run Cell 4 (publish loop).
4. Run Cell 5 (preview + disconnect).

### Workflow D: Check dashboard live counters
1. Return to `notebooks/dashboard.ipynb`.
2. Run Cell 5 (status + disconnect).
3. Return to `notebooks/agent_observer.ipynb`.
4. Run Cell 5 (summary + disconnect).

---

## 3. Expected Output

### Dashboard Cell 2 — Config + topic setup
**Purpose:** Verify map center and topic root come from config.

**Exact expected output (current defaults):**
- `Dashboard config loaded. center=(12.5683, 55.6761), subscribe=simulated-city/pandemic/#`

### Dashboard Cell 4 — Connect and subscribe
**Purpose:** Start read-only live dashboard listener.

**Exact expected output:**
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Subscribed to simulated-city/pandemic/#`
- `Dashboard is live. Run Trigger + Observer notebooks to see updates.`

### Trigger Cell 4 — Feed live stream
**Purpose:** Publish person states for dashboard/observer consumption.

**Expected key lines:**
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Simulation start UTC: 2026-01-01T00:00:00+00:00`
- `step=0000 ...`
- `step=0001 ...`
- `step=0002 ...`
- `step=1439 ...`
- `Phase 3 publish complete. published_messages=432000 topic=simulated-city/pandemic/trigger/person_state`

### Dashboard Cell 5 — Live status summary
**Purpose:** Confirm dashboard consumed raw stream and rendered markers.

**Exact observed output from validation run:**
- `Dashboard status: trigger_messages=1853, exposure_messages=0, snapshot_messages=0, markers=300`
- `Latest snapshot: none`
- `Disconnected from MQTT broker.`

Interpretation:
- `trigger_messages > 0` and `markers=300` confirm map is receiving live trigger data.
- `snapshot_messages=0` can occur if observer snapshot processing lags behind trigger burst.

### Observer Cell 5 — Observer summary
**Purpose:** Confirm observer processed incoming steps and emitted observer topics.

**Exact observed output from validation run:**
- `Observer summary: steps_processed=258, exposure_events_published=0, city_snapshots_published=258, pending_steps=327`
- `Disconnected from MQTT broker.`

Interpretation:
- `steps_processed > 0` and `city_snapshots_published > 0` confirm two-agent + dashboard flow is active.

---

## 4. MQTT Topics

### Dashboard subscriptions (read-only)
- `simulated-city/pandemic/#` (all raw simulation topics)

### Topics consumed and visualized
- `simulated-city/pandemic/trigger/person_state`
  - map marker updates by `person_id`
- `simulated-city/pandemic/observer/exposure_event`
  - exposure counters
- `simulated-city/pandemic/observer/city_snapshot`
  - city-level indicators

### Dashboard publishing
- None (read-only by design).

### Message schemas used by dashboard
Trigger person state:
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

Observer snapshot:
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

### Minimal visual layers for clarity/performance
- Keep one marker layer for persons only.
- Use color by `health_status` (`infected`, `susceptible`, `recovered`).
- Avoid additional heavy layers in Phase 5.

### Common errors and solutions
- **Dashboard map appears but counters stay zero**
  - Verify Trigger Cell 4 is running and publishing.
  - Verify dashboard subscribes to `simulated-city/pandemic/#`.
- **No markers displayed**
  - Confirm Trigger payload has `lat`, `lon`, `person_id`.
  - Check map center from config and zoom level.
- **Frequent reconnect warnings**
  - Confirm broker stability and avoid duplicate client IDs.
  - Run each notebook with unique client suffix (already set in notebooks).

### Verify MQTT flow directly
Use terminal subscriber:
```bash
mosquitto_sub -h 127.0.0.1 -v -t "simulated-city/pandemic/#"
```

You should see Trigger and Observer JSON messages while notebooks run.

---

## 6. Verification Commands

Run from project root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

Expected status:
- `verify_setup.py` passes.
- `validate_structure.py` passes.
- `pytest` passes.
