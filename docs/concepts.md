# Concepts: Simulated City Pandemic Architecture

This document defines the architecture before implementation. It follows the workshop rule that each agent runs in a separate notebook and communicates only through MQTT.

## 1. System Overview

### Trigger Agent (Mobility Producer)
- Technical role: generate person movement state for each simulation step.
- Owns: person position updates, movement randomness, simulation step counter.
- Publishes: current state of each person (position + current health state).
- Does not decide: infection or recovery outcomes.

### Observer Agent (Exposure Detector)
- Technical role: detect potential transmission opportunities from proximity events.
- Owns: pairwise distance checks and exposure event generation.
- Subscribes to person states and computes whether distance is within infection radius.
- Publishes: exposure events and aggregate observation metrics.

### Control Agent (Epidemic State Engine)
- Technical role: apply disease transition rules to person health states.
- Owns: infection probability logic, infection duration tracking, recovery transitions.
- Subscribes to person state + exposure events.
- Publishes: authoritative health state updates for each person.

### Response Agent (Dashboard/Reporting Producer)
- Technical role: convert simulation events into monitoring outputs.
- Owns: city-level counts, trend series, and visualization-ready payloads.
- Subscribes to health updates and observation metrics.
- Publishes: summary metrics for dashboards and map overlays.

---

## 2. MQTT Architecture

All topics are scoped under `simulated-city/pandemic` (or `${mqtt.base_topic}/pandemic` from config).

### Topic Inventory

| Topic | Publisher | Subscribers | Message schema (JSON structure) |
|---|---|---|---|
| `simulated-city/pandemic/trigger/person_state` | Trigger agent | Observer, Control, Response | `{ "step": int, "ts": str, "person_id": str, "lat": float, "lon": float, "health_status": "susceptible\|infected\|recovered" }` |
| `simulated-city/pandemic/observer/exposure_event` | Observer agent | Control, Response | `{ "step": int, "ts": str, "source_id": str, "target_id": str, "distance_m": float, "within_radius": bool }` |
| `simulated-city/pandemic/observer/city_snapshot` | Observer agent | Response, Trigger | `{ "step": int, "ts": str, "population": int, "infected_count": int, "susceptible_count": int, "recovered_count": int }` |
| `simulated-city/pandemic/control/health_update` | Control agent | Trigger, Response | `{ "step": int, "ts": str, "person_id": str, "from_status": str, "to_status": str, "reason": "infection\|recovery", "days_infected": int }` |
| `simulated-city/pandemic/response/metrics` | Response agent | Dashboard notebook (and optional archival consumer) | `{ "step": int, "ts": str, "susceptible": int, "infected": int, "recovered": int, "new_infections": int, "new_recoveries": int }` |

### MQTT Flow Summary
- Trigger emits movement states continuously.
- Observer converts movement states into exposure events.
- Control applies epidemic rules and emits health updates.
- Response aggregates updates into visualization-ready metrics.

---

## 3. Configuration Parameters

The following parameters should live in `config.yaml`.

### MQTT broker settings

| Parameter | Default | Purpose |
|---|---|---|
| `mqtt.active_profiles` | `[local, hivemq_cloud]` | Select active broker profiles (first is primary). |
| `mqtt.profiles.local.host` | `127.0.0.1` | Local broker host. |
| `mqtt.profiles.local.port` | `1883` | Local broker port. |
| `mqtt.profiles.local.tls` | `false` | Local TLS toggle. |
| `mqtt.profiles.hivemq_cloud.host` | `c451c402b7fb41b399936cd5727a1d3f.s1.eu.hivemq.cloud` | Cloud broker host example. |
| `mqtt.profiles.hivemq_cloud.port` | `8883` | Cloud TLS MQTT port. |
| `mqtt.profiles.hivemq_cloud.tls` | `true` | Cloud TLS required. |
| `mqtt.profiles.hivemq_cloud.username_env` | `HIVEMQ_USERNAME` | Env var containing username. |
| `mqtt.profiles.hivemq_cloud.password_env` | `HIVEMQ_PASSWORD` | Env var containing password. |
| `mqtt.client_id_prefix` | `simcity` | Prefix for MQTT client IDs. |
| `mqtt.keepalive_s` | `60` | Keepalive interval in seconds. |
| `mqtt.base_topic` | `simulated-city` | Root topic for all simulation traffic. |

### GPS coordinates / city geometry

| Parameter | Default | Purpose |
|---|---|---|
| `simulation.city_center.lat` | `55.6761` | City center latitude (Copenhagen example). |
| `simulation.city_center.lon` | `12.5683` | City center longitude (Copenhagen example). |
| `simulation.bounds.min_lat` | `55.62` | Southern simulation boundary. |
| `simulation.bounds.max_lat` | `55.72` | Northern simulation boundary. |
| `simulation.bounds.min_lon` | `12.48` | Western simulation boundary. |
| `simulation.bounds.max_lon` | `12.66` | Eastern simulation boundary. |

### Thresholds and limits

| Parameter | Default | Purpose |
|---|---|---|
| `simulation.population_size` | `300` | Number of simulated persons. |
| `simulation.initial_infected` | `5` | Initial infected population. |
| `simulation.infection_radius_m` | `2.0` | Distance threshold for transmission eligibility. |
| `simulation.infection_probability` | `0.5` | Infection chance when inside infection radius. |
| `simulation.recovery_days` | `10` | Days before infected person can recover. |
| `simulation.max_speed_m_per_s` | `1.4` | Movement speed cap for realistic pedestrian motion. |

### Timing parameters

| Parameter | Default | Purpose |
|---|---|---|
| `simulation.time_step_s` | `1.0` | Wall-clock delay between simulation iterations. |
| `simulation.simulated_hours_per_step` | `0.25` | Simulated time advanced per step. |
| `simulation.publish_every_n_steps` | `1` | Publish frequency control. |
| `simulation.total_steps` | `1440` | Total steps (15 simulated days at 0.25 h/step). |
| `simulation.seed` | `42` | Deterministic random seed for reproducibility. |

---

## 4. Architecture Decisions

### Notebooks to Create

- `notebooks/agent_trigger.ipynb`
  - Purpose: person creation and movement updates; publish person states.
- `notebooks/agent_observer.ipynb`
  - Purpose: subscribe to person states; detect proximity exposures; publish exposure events + city snapshot.
- `notebooks/agent_control.ipynb`
  - Purpose: subscribe to exposure/person state streams; apply infection/recovery transitions; publish health updates.
- `notebooks/agent_response.ipynb`
  - Purpose: subscribe to control/observer outputs; produce metrics and map/dashboard payloads.
- `notebooks/dashboard.ipynb`
  - Purpose: read-only monitoring notebook using anymap-ts and metric charts from MQTT topics.

### Library Code (`src/simulated_city/`)

#### Data models (dataclasses)
- `PersonState`: person identity, coordinates, and health state.
- `ExposureEvent`: source-target pair, distance, and step metadata.
- `HealthTransition`: from/to health state and transition reason.
- `CityMetrics`: susceptible/infected/recovered counts and deltas.
- `SimulationParams`: thresholds, timing, and bounds loaded from config.

#### Utility functions
- Topic naming helpers (`build_topic(base_topic, domain, event)`).
- Payload validation helpers (`validate_person_state`, `validate_exposure_event`).
- Time and step helpers (timestamp generation, step-to-day conversion).
- Config extraction helpers for simulation-specific keys.

#### Calculation helpers
- Distance calculation (meters between lat/lon points).
- Infection decision function (radius + probability rule).
- Recovery eligibility function (days infected threshold).
- Aggregate metric calculators from person-level states.

### Classes vs Functions

#### Model as classes
- Agent runtimes with stateful subscriptions and caches:
  - `TriggerAgent`, `ObserverAgent`, `ControlAgent`, `ResponseAgent`.
- Dataclasses for typed payloads and config structures.
- Optional orchestrator class for lifecycle start/stop in local testing.

#### Keep as simple functions
- Pure calculations (distance, probability checks, aggregates).
- Stateless transformations (dataclass ↔ JSON payload).
- Topic construction and small validation utilities.
- Config-to-parameter mapping utilities.

Rationale: classes hold long-lived state and MQTT client behavior; functions keep math and transformations easy to test and reason about.

---

## 5. Open Questions

- Should infection be evaluated only by the Control agent, or partly by Observer (Observer currently emits eligibility, not final infection)? The infection shoould be evaluated by both the control agent and also the observer
- Is recovery deterministic exactly at `recovery_days`, or probabilistic after that threshold? The recovery deterministic exactly at recover_days.
- Should city boundaries wrap around (torus) or reflect/clip movement at edges? it should reflect movement at edges
- Does one simulation step represent one second, one minute, or configurable simulated time independent of wall-clock sleep? every step is 0.25 hours
- Should the dashboard subscribe to all raw topics or only consolidated `response/metrics`?
- Should response outputs include neighborhood-level metrics, or only city-wide totals?
- The docs currently mention helper names like `connect_mqtt` / `publish_json_checked`, while current library code also exposes connector/publisher classes; which API should be canonical for notebooks?

These assumptions are intentionally explicit so they can be validated before implementation planning.