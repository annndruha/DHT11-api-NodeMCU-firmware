import logging

from fastapi import APIRouter
from fastapi_sqlalchemy import db
from pydantic import constr

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Devices
from temperature_monitor_api.utils.utils import object_as_dict

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get('/devices')
async def get_devices_list(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1)
):
    if access_token != settings.ACCESS_TOKEN:
        return {"success": False, "detail": 'Unauthorized. Given access_token not accepted'}

    devices: Devices = db.session.query(Devices)

    devices_list = []
    for measurement in devices.all():
        devices_list.append(object_as_dict(measurement))

    if len(devices_list):
        return {"success": True, "devices": devices_list}
    else:
        return {"success": False, "detail": 'Data not found'}


@router.post('/device')
def add_device(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1),
        device_id: constr(strip_whitespace=True, min_length=1)
):
    if access_token != settings.ACCESS_TOKEN:
        return {"success": False, "detail": 'Unauthorized. Given access_token not accepted'}

    devices: Devices = db.session.query(Devices)

    device_exist: Devices = (devices.filter(Devices.device_id == device_id)).one_or_none()
    if device_exist:
        return {"success": False, "detail": 'Device already exist'}
    else:
        db.session.add(Devices(device_id=device_id))
        db.session.flush()
        db.session.commit()
        return {"success": True}
