from datetime import datetime
from pydantic import BaseModel


# Pydantic Models
class SensorData(BaseModel):
    tem: float
    hum: float
    light: int
    led: bool
    fan: bool
    tiny: float
    timestamp: datetime

class ControlRequest(BaseModel):
    led_state: bool
    fan_state: bool

class SensorDataResponse(BaseModel):
    tem: float
    hum: float
    light: int
    led: bool
    fan: bool
    tiny: float
    timestamp: str