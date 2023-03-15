import logging
import time

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from pydantic import constr

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Devices
from temperature_monitor_api.utils.utils import object_as_dict

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get(
    '/devices',
    status_code=200,
    responses={
        404: {'detail': 'Data not found'},
    },
)
async def get_devices_list(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1)
):
    if access_token != settings.ACCESS_TOKEN:
        raise HTTPException(401, 'Unauthorized. Given access_token not accepted')

    devices: Devices = db.session.query(Devices)

    devices_list = []
    for measurement in devices.all():
        devices_list.append(object_as_dict(measurement))

    if len(devices_list):
        return {"success": True, "devices": devices_list}
    else:
        return {"success": False, "detail": 'Data not found'}


# @router.post('/measurements')
# def set_measurements(
#         access_token: constr(strip_whitespace=True, to_upper=True, min_length=1),
#         temperature: float,
#         humidity: float
# ):
#     if access_token != settings.ACCESS_TOKEN:
#         raise HTTPException(401, 'Unauthorized. Given access_token not accepted')
#
#     db.session.add(
#         Measurements(
#             unix_id=int(time.time()),
#             device_id='1',
#             temperature=temperature,
#             humidity=humidity
#         )
#     )
#     db.session.flush()
#     db.session.commit()
#     return {"success": True}
