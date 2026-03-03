"""simulated_city

This package intentionally keeps only workshop-agnostic helpers:
- YAML/.env configuration loading (see :mod:`simulated_city.config`)
- MQTT connection helpers (see :mod:`simulated_city.mqtt`)

Simulation logic is meant to be implemented by students during the workshop.
"""

from .config import AppConfig, MqttConfig, load_config
from .geo import (
	EPSG_25832,
	EPSG_3857,
	epsg25832_to_webmercator,
	transform_many,
	transform_xy,
	webmercator_to_epsg25832,
	wgs2utm,
	utm2wgs,
)
from .mqtt import MqttConnector, MqttPublisher
from .epidemic import (
	VALID_HEALTH_STATES,
	build_health_update,
	build_response_metrics,
	can_transition,
	days_infected,
	parse_exposure_event,
	parse_person_state,
	recovery_steps,
)

__all__ = [
	"AppConfig",
	"MqttConfig",
	"load_config",
	"EPSG_25832",
	"EPSG_3857",
	"transform_xy",
	"transform_many",
	"webmercator_to_epsg25832",
	"epsg25832_to_webmercator",
	"wgs2utm",
	"utm2wgs",
	"MqttConnector",
	"MqttPublisher",
	"VALID_HEALTH_STATES",
	"parse_person_state",
	"parse_exposure_event",
	"build_health_update",
	"build_response_metrics",
	"can_transition",
	"recovery_steps",
	"days_infected",
]
