from datetime import datetime
from typing import List

from pydantic import constr, BaseModel


# General Schemas
class SuccessResponseSchema(BaseModel):
    detail: str = 'Some message'


class ErrorResponseSchema(BaseModel):
    error: str = 'Some error explanation'


class ForbiddenSchema(BaseModel):
    detail: str = 'Unauthorized. Given ADMIN_TOKEN not accepted'


# Device Schemas
class DeviceSchema(BaseModel):
    device_id: int = 42
    device_name: constr(strip_whitespace=True, min_length=3) = "my_device_name"
    device_token: str = "UPPERCASE_TOKEN"
    created_date: datetime


class ListDevicesSchema(BaseModel):
    devices: List[DeviceSchema]


# Measurements Schemas
class MeasurementSchema(BaseModel):
    primary_key: int
    timestamp: datetime
    device_id: int
    temperature: float
    humidity: float


class ListMeasurementsSchema(BaseModel):
    length: int
    timestamps: List[datetime]
    temperatures: List[float]
    humiditys: List[float]
