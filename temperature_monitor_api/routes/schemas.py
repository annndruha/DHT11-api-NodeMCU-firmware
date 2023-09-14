from datetime import datetime
from typing import List, Dict, Literal

from pydantic import constr, BaseModel


# General Schemas
class SuccessResponseSchema(BaseModel):
    detail: str = 'Some message'


class ErrorResponseSchema(BaseModel):
    error: str = 'Some error explanation'


class ForbiddenSchema(BaseModel):
    detail: str = 'Unauthorized. Given ADMIN_TOKEN not accepted'


# Device Schemas
class DeviceCompleteSchema(BaseModel):
    device_id: int = 42
    device_name: constr(strip_whitespace=True, min_length=3) = "my_device_name"
    device_token: str = "UPPERCASE_TOKEN"
    created_date: datetime


class DeviceIncompleteSchema(BaseModel):
    device_name: constr(strip_whitespace=True, min_length=3) = "my_device_name"
    created_date: datetime


class ListDevicesSchema(BaseModel):
    devices: List[DeviceIncompleteSchema]


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


class ChatJsItem(BaseModel):
    x: str = "2023-09-14 14:57:17"
    y: float = "25.1"


class ListMeasurementsChatJsSchema(BaseModel):
    temperatures: List[ChatJsItem]
    humiditys: List[ChatJsItem]
