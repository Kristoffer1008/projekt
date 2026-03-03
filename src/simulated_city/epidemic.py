from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any


VALID_HEALTH_STATES = {"susceptible", "infected", "recovered"}


@dataclass(frozen=True, slots=True)
class PersonStateMessage:
    step: int
    ts: str
    person_id: str
    lat: float
    lon: float
    health_status: str


@dataclass(frozen=True, slots=True)
class ExposureEventMessage:
    step: int
    ts: str
    source_id: str
    target_id: str
    distance_m: float
    within_radius: bool


@dataclass(frozen=True, slots=True)
class HealthUpdateMessage:
    step: int
    ts: str
    person_id: str
    from_status: str
    to_status: str
    reason: str
    days_infected: float


@dataclass(frozen=True, slots=True)
class ResponseMetricsMessage:
    step: int
    ts: str
    susceptible: int
    infected: int
    recovered: int
    new_infections: int
    new_recoveries: int


def _require_keys(data: dict[str, Any], keys: list[str], payload_name: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{payload_name} missing required keys: {', '.join(missing)}")


def parse_person_state(data: dict[str, Any]) -> PersonStateMessage:
    _require_keys(data, ["step", "ts", "person_id", "lat", "lon", "health_status"], "person_state")
    health_status = str(data["health_status"])
    if health_status not in VALID_HEALTH_STATES:
        raise ValueError(f"person_state health_status must be one of {sorted(VALID_HEALTH_STATES)}")

    return PersonStateMessage(
        step=int(data["step"]),
        ts=str(data["ts"]),
        person_id=str(data["person_id"]),
        lat=float(data["lat"]),
        lon=float(data["lon"]),
        health_status=health_status,
    )


def parse_exposure_event(data: dict[str, Any]) -> ExposureEventMessage:
    _require_keys(data, ["step", "ts", "source_id", "target_id", "distance_m", "within_radius"], "exposure_event")
    return ExposureEventMessage(
        step=int(data["step"]),
        ts=str(data["ts"]),
        source_id=str(data["source_id"]),
        target_id=str(data["target_id"]),
        distance_m=float(data["distance_m"]),
        within_radius=bool(data["within_radius"]),
    )


def build_health_update(
    *,
    step: int,
    ts: str,
    person_id: str,
    from_status: str,
    to_status: str,
    reason: str,
    days_infected: float,
) -> dict[str, Any]:
    return {
        "step": int(step),
        "ts": str(ts),
        "person_id": str(person_id),
        "from_status": str(from_status),
        "to_status": str(to_status),
        "reason": str(reason),
        "days_infected": float(days_infected),
    }


def build_response_metrics(
    *,
    step: int,
    ts: str,
    susceptible: int,
    infected: int,
    recovered: int,
    new_infections: int,
    new_recoveries: int,
) -> dict[str, Any]:
    return {
        "step": int(step),
        "ts": str(ts),
        "susceptible": int(susceptible),
        "infected": int(infected),
        "recovered": int(recovered),
        "new_infections": int(new_infections),
        "new_recoveries": int(new_recoveries),
    }


def can_transition(from_status: str, to_status: str) -> bool:
    from_state = str(from_status)
    to_state = str(to_status)
    if from_state not in VALID_HEALTH_STATES or to_state not in VALID_HEALTH_STATES:
        return False
    if from_state == to_state:
        return True
    return (from_state, to_state) in {
        ("susceptible", "infected"),
        ("infected", "recovered"),
    }


def recovery_steps(recovery_days: int, simulated_hours_per_step: float) -> int:
    if recovery_days <= 0:
        return 0
    if simulated_hours_per_step <= 0:
        raise ValueError("simulated_hours_per_step must be > 0")
    total_hours = recovery_days * 24.0
    return int(ceil(total_hours / simulated_hours_per_step))


def days_infected(current_step: int, infected_since_step: int, simulated_hours_per_step: float) -> float:
    step_delta = max(0, int(current_step) - int(infected_since_step))
    return (step_delta * float(simulated_hours_per_step)) / 24.0
