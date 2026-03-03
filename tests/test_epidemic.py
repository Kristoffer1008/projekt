from simulated_city.epidemic import (
    build_health_update,
    build_response_metrics,
    can_transition,
    days_infected,
    parse_exposure_event,
    parse_person_state,
    recovery_steps,
)


def test_parse_person_state_valid() -> None:
    payload = {
        "step": 1,
        "ts": "2026-01-01T00:00:00+00:00",
        "person_id": "person-001",
        "lat": 55.67,
        "lon": 12.56,
        "health_status": "susceptible",
    }
    msg = parse_person_state(payload)
    assert msg.person_id == "person-001"
    assert msg.health_status == "susceptible"


def test_parse_exposure_event_valid() -> None:
    payload = {
        "step": 2,
        "ts": "2026-01-01T00:15:00+00:00",
        "source_id": "person-000",
        "target_id": "person-005",
        "distance_m": 1.25,
        "within_radius": True,
    }
    msg = parse_exposure_event(payload)
    assert msg.step == 2
    assert msg.within_radius is True


def test_can_transition_one_way_rules() -> None:
    assert can_transition("susceptible", "infected")
    assert can_transition("infected", "recovered")
    assert can_transition("recovered", "recovered")
    assert not can_transition("recovered", "infected")
    assert not can_transition("recovered", "susceptible")


def test_recovery_steps_and_days_infected() -> None:
    assert recovery_steps(recovery_days=10, simulated_hours_per_step=0.25) == 960
    assert days_infected(current_step=960, infected_since_step=0, simulated_hours_per_step=0.25) == 10.0


def test_builders_return_expected_keys() -> None:
    health = build_health_update(
        step=12,
        ts="2026-01-01T03:00:00+00:00",
        person_id="person-010",
        from_status="susceptible",
        to_status="infected",
        reason="infection",
        days_infected=0.0,
    )
    assert health["to_status"] == "infected"

    metrics = build_response_metrics(
        step=12,
        ts="2026-01-01T03:00:00+00:00",
        susceptible=290,
        infected=10,
        recovered=0,
        new_infections=3,
        new_recoveries=0,
    )
    assert metrics["new_infections"] == 3
