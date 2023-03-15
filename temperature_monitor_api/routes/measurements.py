import logging
import time
import datetime
from typing import List, Optional

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from pydantic import constr
from sqlalchemy import and_, func, or_
from sqlalchemy import inspect

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Measurements

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@router.get(
    '/measurements',
    status_code=200,
    responses={
        404: {'detail': 'Data not found'},
    },
)
async def get_measurements(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1)
):
    if access_token != settings.ACCESS_TOKEN:
        raise HTTPException(401, 'Unauthorized. Given access_token not accepted')

    measurements: Measurements = db.session.query(Measurements)

    measurements_list = []

    for measurement in measurements.all():
        measurements_list.append(object_as_dict(measurement))

    if len(measurements_list):
        return {"success": True, "measurements": measurements_list}
    else:
        return {"success": False, "detail": 'Data not found'}


@router.get(
    '/measurements_flat',
    status_code=200,
    responses={
        404: {'detail': 'Data not found'},
    },
)
async def get_measurements_flat(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1)
):
    if access_token != settings.ACCESS_TOKEN:
        raise HTTPException(401, 'Unauthorized. Given access_token not accepted')

    measurements: Measurements = db.session.query(Measurements)

    measurements_flat = {"unix_ids": [], "timestamps": [], "device_ids": [],
                         "temperatures": [], "humiditys": []}
    for measurement in measurements.all():
        measurements_flat['unix_ids'].append(measurement.unix_id)
        measurements_flat['timestamps'].append(measurement.timestamp)
        measurements_flat['device_ids'].append(measurement.device_id)
        measurements_flat['temperatures'].append(measurement.temperature)
        measurements_flat['humiditys'].append(measurement.humidity)

    measurements_flat['length'] = len(measurements_flat['unix_ids'])
    if len(measurements_flat['unix_ids']):
        return {"success": True, "measurements_flat": measurements_flat}
    else:
        return {"success": False, "detail": 'Data not found'}


@router.post('/measurements')
def set_measurements(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1),
        temperature: float,
        humidity: float
):
    if access_token != settings.ACCESS_TOKEN:
        raise HTTPException(401, 'Unauthorized. Given access_token not accepted')

    db.session.add(
        Measurements(
            unix_id=int(time.time()),
            device_id='1',
            temperature=temperature,
            humidity=humidity
        )
    )
    db.session.flush()
    db.session.commit()
    return {"success": True}
