# Exercises

This guide shows how to build a multi-agent simulation using separate MQTT-communicating notebooks.

## Phase 1: Minimal Working Example (Single Agent, No MQTT)

Create `notebooks/agent_trigger.ipynb` as a **single Trigger agent** notebook with local in-memory simulation only.

### Phase 1 scope

- Load configuration via `simulated_city.config.load_config()`.
- Initialize local person states with deterministic randomness.
- Run a movement loop with boundary reflection.
- Track local `health_status` values in memory.
- Do not connect to MQTT and do not publish/subscribe in this phase.

### Recommended cell order

1. **Setup cell**
    - Import `load_config`, standard library utilities, and dataclass support.
    - Load config and print active seed/delay values.
2. **Initialization cell**
    - Create a local `PersonState` model.
    - Initialize persons and set one person to `infected`, remaining to `susceptible`.
3. **Simulation loop cell**
    - Apply deterministic movement.
    - Reflect movement at boundaries.
    - Print per-step local summary (`susceptible`, `infected`, `recovered`).
4. **Schema preview cell**
    - Print one local dictionary payload shape for a future publishing step.
    - Keep this local-only; no MQTT call in Phase 1.

### Phase 1 checklist

- [ ] Notebook contains one agent only (`agent_trigger.ipynb`).
- [ ] Config is loaded via `simulated_city.config.load_config()`.
- [ ] No MQTT usage appears in notebook code.
- [ ] Boundary reflection is observable in step output.
- [ ] Local person schema preview is printed.

## Phase 3: Trigger Agent MQTT Publishing

Update `notebooks/agent_trigger.ipynb` so the Trigger agent publishes person-state updates.

### Phase 3 scope

- Connect with `mqtt.connect_mqtt(mqtt_cfg)`.
- Publish each person state with `mqtt.publish_json_checked(client, topic, data)`.
- Topic must be: `${mqtt.base_topic}/pandemic/trigger/person_state`.
- Payload must include: `step`, `ts`, `person_id`, `lat`, `lon`, `health_status`.

### Recommended cell order

1. **Config + MQTT setup cell**
    - Load config with `load_config()`.
    - Resolve `mqtt_cfg` and Trigger topic string.
2. **Initialization cell**
    - Build initial in-memory persons from simulation config.
3. **Publish loop cell**
    - Connect to MQTT.
    - Move persons and publish each person-state payload per publish cadence.
4. **Cleanup cell**
    - Print one final payload preview.
    - Disconnect client cleanly.

### Phase 3 checklist

- [ ] Notebook still represents one agent only.
- [ ] Uses `mqtt.connect_mqtt()` to connect.
- [ ] Uses `mqtt.publish_json_checked()` for publishing.
- [ ] Publishes to `${mqtt.base_topic}/pandemic/trigger/person_state`.
- [ ] Payload contains required keys (`step`, `ts`, `person_id`, `lat`, `lon`, `health_status`).

## Phase 4: Observer Agent Subscription and Exposure Detection

Create `notebooks/agent_observer.ipynb` as a separate Observer agent notebook.

### Phase 4 scope

- Subscribe to `${mqtt.base_topic}/pandemic/trigger/person_state`.
- Buffer person-state messages by step.
- Compute pairwise distances between infected and susceptible persons.
- Publish exposure candidates to `${mqtt.base_topic}/pandemic/observer/exposure_event`.
- Publish city snapshots to `${mqtt.base_topic}/pandemic/observer/city_snapshot`.
- Keep health transitions out of Observer (Control owns state transitions in later phases).

### Multi-notebook run steps

1. Open `notebooks/agent_observer.ipynb` and run Cells 1–4 (Observer starts listening).
2. Open `notebooks/agent_trigger.ipynb` and run Cells 1–4 (Trigger publishes person states).
3. Return to `notebooks/agent_observer.ipynb` and run Cell 5 (summary + disconnect).

### Phase 4 checklist

- [ ] Observer uses `mqtt.connect_mqtt()` and `mqtt.publish_json_checked()`.
- [ ] Observer subscribes to Trigger person-state topic.
- [ ] Observer publishes exposure events with required keys.
- [ ] Observer publishes city snapshots for completed steps.
- [ ] Trigger and Observer run as separate notebooks/processes.

## Principle: Many Small Notebooks, Not One Big File

Each agent or component is a **separate notebook** that:
- Runs its own simulation logic in a loop
- Publishes state to MQTT topics
- Subscribes to input from other agents via MQTT

This is how real systems work — agents are independent processes.

## Example Structure

```
notebooks/
├── agent_transport.ipynb      # Transport simulation agent
├── agent_environment.ipynb    # Air quality simulation agent  
├── agent_infrastructure.ipynb # Building/utility agent
└── dashboard.ipynb            # Read-only visualization
```

## Exercise 1: Single Agent with MQTT

Create `notebooks/agent_transport.ipynb`:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from time import sleep
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Connect to MQTT
client = mqtt.connect_mqtt(mqtt_cfg)

# Cell 3: Simulation loop (run this cell repeatedly or schedule it)
for step in range(100):
    vehicle_count = 50 + step % 20  # Simple simulation
    traffic_data = {
        "step": step,
        "vehicles_on_road": vehicle_count,
        "avg_speed_kmh": 45 - (vehicle_count / 10)
    }
    
    # Publish to MQTT
    mqtt.publish_json_checked(
        client, 
        f"{mqtt_cfg.base_topic}/transport/status", 
        traffic_data
    )
    
    sleep(1)
```

**Key points:**
1. Each notebook is independent
2. Configuration is loaded from `config.yaml`
3. Uses `mqtt.connect_mqtt()` and `mqtt.publish_json_checked()`
4. Publishes to a unique topic like `base_topic/transport/status`

## Exercise 2: Multiple Agents (Distributed Simulation)

Create `notebooks/agent_environment.ipynb` that **reads** transport data and **publishes** air quality:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from time import sleep
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Subscribe to transport data
def on_transport_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"Transport vehicles: {payload['vehicles_on_road']}")
    # Store in a variable for use

latest_vehicle_count = 0

def on_message(client, userdata, msg):
    global latest_vehicle_count
    if "transport" in msg.topic:
        payload = json.loads(msg.payload.decode())
        latest_vehicle_count = payload['vehicles_on_road']

# Cell 3: Connect and subscribe
client = mqtt.connect_mqtt(mqtt_cfg)
client.on_message = on_message
client.subscribe(f"{mqtt_cfg.base_topic}/transport/status")

# Cell 4: Simulation loop (depends on transport data)
for step in range(100):
    # Air quality = function of vehicle count
    pm25 = 10 + (latest_vehicle_count * 0.5)  # Vehicles → pollution
    
    air_quality = {
        "step": step,
        "pm25_ug_m3": pm25,
        "vehicles_detected": latest_vehicle_count
    }
    
    mqtt.publish_json_checked(
        client,
        f"{mqtt_cfg.base_topic}/environment/air_quality",
        air_quality
    )
    
    sleep(1)
```

## Exercise 3: Dashboard with `anymap-ts`

Create `notebooks/dashboard.ipynb` to visualize both agents:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from anymap_ts.jupyter import IPythonDisplay
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Create map
map_display = IPythonDisplay(center=[51.5, -0.1], zoom=12)
map_display.show()

# Cell 3: Update map from MQTT
latest_data = {"transport": {}, "environment": {}}

def on_message(client, userdata, msg):
    global latest_data
    payload = json.loads(msg.payload.decode())
    
    if "transport" in msg.topic:
        latest_data["transport"] = payload
    elif "environment" in msg.topic:
        latest_data["environment"] = payload
    
    # Update map
    update_display()

def update_display():
    # Clear and redraw markers
    map_display.clear()
    
    if latest_data.get("transport"):
        vehicles = latest_data["transport"].get("vehicles_on_road", 0)
        map_display.add_marker(
            [51.5, -0.1],
            properties={"title": f"Vehicles: {vehicles}"}
        )

# Cell 4: Connect and subscribe
client = mqtt.connect_mqtt(mqtt_cfg)
client.on_message = on_message
client.subscribe(f"{mqtt_cfg.base_topic}/#")  # Subscribe to all

# Cell 5: Keep listening
import time
while True:
    time.sleep(1)
```

## Checklist Before Submitting

- [ ] Each agent is a **separate notebook** (not one giant file)
- [ ] Each notebook publishes to a unique MQTT topic
- [ ] Dashboard or main notebook **subscribes** to agent topics
- [ ] Used `anymap-ts` for visualization (not `folium` or `matplotlib`)
- [ ] Used `mqtt.connect_mqtt()` and `mqtt.publish_json_checked()`
- [ ] Configuration loaded via `config.load_config()`
- [ ] Ran `python scripts/verify_setup.py` (all ✅)
- [ ] All dependencies in `pyproject.toml` (no inline `pip install`)

## Common Mistakes

**Mistake:** One notebook with all simulation code  
**Fix:** Split into agent notebooks that communicate via MQTT

**Mistake:** Using `folium` or `matplotlib` for real-time data  
**Fix:** Use `anymap-ts` which is built for live MQTT feeds

**Mistake:** Hardcoded MQTT settings in notebook  
**Fix:** Use `config.load_config()` to load from `config.yaml`

**Mistake:** Installing packages inside notebooks with `!pip install`  
**Fix:** Add to `pyproject.toml` and reinstall with `pip install -e ".[notebooks]"`
