# Phase 3 Runtime Guide (Instructor Validation)

This guide validates Phase 3 only: the Trigger agent connects to MQTT and publishes person-state messages to the Phase 3 topic contract.

## 1. What Was Created

### Notebooks/Scripts
- Updated notebook: `notebooks/agent_trigger.ipynb`

### Library modules added to `src/simulated_city/`
- No new module files created.
- Updated existing MQTT helpers in `src/simulated_city/mqtt.py`:
  - `connect_mqtt(mqtt_cfg)`
  - `publish_json_checked(client, topic, data)`

### Configuration changes (`config.yaml` entries)
- No new Phase 3 config keys were required.
- Existing `mqtt.*` and `simulation.*` keys are used by the notebook.

Updated documentation:
- `docs/mqtt.md`
- `docs/exercises.md`

---

## 2. How to Run

### Workflow A: Run Trigger publisher notebook
1. Open `notebooks/agent_trigger.ipynb`.
2. Run Cell 1 (overview).
3. Run Cell 2 (config + MQTT target setup).
4. Run Cell 3 (initialize local person states).
5. Run Cell 4 (connect and publish loop).
6. Run Cell 5 (final payload preview + disconnect).

Observe output:
- Cell 2 prints config summary and target MQTT topic.
- Cell 4 prints connection confirmation, sample simulation lines, and final publish count.
- Cell 5 prints final payload preview and disconnect confirmation.

### Workflow B: Verify broker receives messages (terminal)
1. Open a terminal at project root.
2. Run:
   ```bash
   mosquitto_sub -h 127.0.0.1 -t "simulated-city/pandemic/trigger/person_state" -v
   ```
3. Start notebook workflow A and execute Cell 4.
4. Observe incoming JSON messages in terminal from Trigger publisher.

---

## 3. Expected Output

### Cell 2 — Config + topic setup
**Purpose:** Confirm simulation + MQTT target are loaded from config.

**Exact expected output (current defaults):**
- `Loaded config. seed=42, population=300, steps=1440, publish_every_n_steps=1`
- `MQTT target: 127.0.0.1:1883 topic=simulated-city/pandemic/trigger/person_state`

**If different:**
- Different values can be valid if `config.yaml` was intentionally changed.
- Missing topic text indicates wrong notebook topic construction.

### Cell 3 — Initialize persons
**Purpose:** Prepare person-state population for publishing.

**Exact expected output (current defaults):**
- `Initialized 300 persons. infected=5, susceptible=295, delta_scale=0.00001261`

**If different:**
- Count mismatch indicates config mismatch or initialization regression.

### Cell 4 — Connect + publish loop
**Purpose:** Publish each person-state payload to MQTT topic contract.

**Exact expected output (current defaults):**
- `Connected to MQTT broker at 127.0.0.1:1883`
- `Simulation start UTC: 2026-01-01T00:00:00+00:00`
- `step=0000 sample=person-000 lat=55.683937 lon=12.484495 susceptible=295 infected=5 recovered=0`
- `step=0001 sample=person-000 lat=55.683931 lon=12.484488 susceptible=295 infected=5 recovered=0`
- `step=0002 sample=person-000 lat=55.683926 lon=12.484481 susceptible=295 infected=5 recovered=0`
- `step=1439 sample=person-000 lat=55.675771 lon=12.485552 susceptible=295 infected=5 recovered=0`
- `Phase 3 publish complete. published_messages=432000 topic=simulated-city/pandemic/trigger/person_state`

Why `432000`:
- `population_size=300`
- `total_steps=1440`
- `publish_every_n_steps=1`
- publishes = `300 * 1440 = 432000`

**If different:**
- Lower publish count indicates changed cadence or interrupted loop.
- Connection failure indicates broker unavailable or auth mismatch.

### Cell 5 — Final payload preview + disconnect
**Purpose:** Show final message shape and close connection.

**Exact expected output (current defaults):**
- `{'step': 1439, 'ts': '2026-01-15T23:45:00+00:00', 'person_id': 'person-000', 'lat': 55.675771, 'lon': 12.485552, 'health_status': 'infected'}`
- `Disconnected from MQTT broker.`

**If different:**
- Missing keys indicates schema drift from contract.
- Missing disconnect line indicates cleanup did not run.

---

## 4. MQTT Topics

### Published topics
- `simulated-city/pandemic/trigger/person_state`
  - Publisher: `notebooks/agent_trigger.ipynb`
  - Data: one message per person per publish step

### Subscribed topics
- None in Phase 3.

### Message schema
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

---

## 5. Debugging Guidance

### Increase verbosity
- In notebook Cell 4, temporarily print every `payload` before publish.
- Set `publish_every_n_steps` higher (e.g., `60`) in `config.yaml` to reduce message load during debugging.

### Common errors and solutions
- **`RuntimeError: Could not connect to MQTT broker ...`**
  - Start local broker and confirm `mqtt.profiles.local.host/port` in `config.yaml`.
- **`RuntimeError: MQTT publish failed ...`**
  - Check broker availability and topic permissions.
- **No messages in `mosquitto_sub`**
  - Verify you subscribe to `simulated-city/pandemic/trigger/person_state`.
  - Confirm notebook Cell 4 completed and printed publish count.

### Verify MQTT flow
- Keep `mosquitto_sub` running while executing notebook Cell 4.
- Confirm continuous incoming JSON with expected keys.

---

## 6. Verification Commands

Run from project root:

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

Interpretation:
- `verify_setup.py` should pass.
- `validate_structure.py` should not flag missing MQTT connect for Trigger notebook in Phase 3.
- `pytest` should pass in environments with valid broker profile access; failures tied to external broker auth are environment issues, not Trigger publish-loop logic.
