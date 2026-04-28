from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class Topic(str, Enum):
    MATERIAL = "material"
    PRODUCTION = "production"
    QUALITY = "quality"
    MAINTENANCE = "maintenance"
    LOGISTICS = "logistics"
    PLANNING = "planning"
    ORDER = "order"
    METRICS = "metrics"
    SYSTEM = "system"


class StationStatus(str, Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    WAITING_MATERIAL = "WAITING_MATERIAL"
    BROKEN = "BROKEN"
    MAINTENANCE = "MAINTENANCE"


class AGVStatus(str, Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    LOADING = "LOADING"
    UNLOADING = "UNLOADING"


class MaintenanceStatus(str, Enum):
    IDLE = "IDLE"
    MOVING_TO_SITE = "MOVING_TO_SITE"
    REPAIRING = "REPAIRING"


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int
    source_id: str
    topic: Topic
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}


class SimConfig(BaseModel):
    tick_duration_minutes: int = 1
    max_ticks: int = 1440
    station_failure_rate: float = 0.002
    base_yield_rate: float = 0.98
    agv_speed_ticks_per_unit: float = 0.5
    mttr_ticks: int = 30
