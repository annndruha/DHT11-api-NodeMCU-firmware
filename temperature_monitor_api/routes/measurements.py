import math
import logging
import datetime
from typing import Optional

from pydantic import constr
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from fastapi.responses import JSONResponse

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Devices, Measurements
from temperature_monitor_api.utils.utils import object_as_dict
from temperature_monitor_api.routes.auth import AdminAuth
from temperature_monitor_api.routes.schemas import SuccessResponseSchema, ErrorResponseSchema, ForbiddenSchema, \
    MeasurementSchema, ListMeasurementsSchema

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post('/create_measurement', responses={200: {"model": SuccessResponseSchema},
                                               400: {"model": ErrorResponseSchema}})
def add_new_measurement(
        device_token: str,
        temperature: float,
        humidity: float
):
    """
    Add a new measurement item to database.
    Warning: if temperature and humidity same as last point, it will not be added.
    But when values change, it added two points: last with new timestamp and new.
    This need to save disk space.
    """
    device: Devices = db.session.query(Devices).filter(Devices.device_token == device_token).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device not existed or token is wrong.'}, 400)

    if math.isnan(temperature) or math.isnan(humidity):
        return JSONResponse({"error": 'Received NaN. Request skipped'}, 400)

    device_measurements = db.session.query(Measurements).filter(Measurements.device_id == device.device_id)
    last_measurement = device_measurements.order_by(Measurements.timestamp.desc()).first()

    if last_measurement is None:
        db.session.add(Measurements(device_id=device.device_id, temperature=temperature, humidity=humidity))
        db.session.flush()
        db.session.commit()
        return {"detail": 'Added. Cool start!'}

    if last_measurement.temperature == temperature and last_measurement.humidity == humidity:
        now_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        delta = now_time.replace(tzinfo=None) - last_measurement.timestamp + datetime.timedelta(seconds=1)
        if delta <= datetime.timedelta(minutes=1):
            return {"detail": f'Skipped. Same as last and time <1min since last: {delta}'}

    # db.session.add(Measurements(device_id=device.device_id,
    #                             temperature=last_measurement.temperature,
    #                             humidity=last_measurement.humidity))
    # db.session.flush()
    # db.session.commit()
    db.session.add(Measurements(device_id=device.device_id,
                                temperature=temperature,
                                humidity=humidity))
    db.session.flush()
    db.session.commit()
    return {"detail": 'Added'}


@router.get('/get_measurement', responses={200: {"model": MeasurementSchema},
                                           400: {"model": ErrorResponseSchema},
                                           403: {"model": ForbiddenSchema}})
async def get_one_measurement(
        primary_key: int,
        admin_token=Depends(AdminAuth())
):
    """
    Get a specific measurement by primary key
    """
    measurement = db.session.query(Measurements).filter(Measurements.primary_key == primary_key).one_or_none()
    if not measurement:
        return JSONResponse({"error": 'Measurement with this id is not existed'}, 400)

    return object_as_dict(measurement)


@router.get('/list_measurements',
            responses={200: {"model": ListMeasurementsSchema},
                       400: {"model": ErrorResponseSchema},
                       403: {"model": ForbiddenSchema}})
async def list_measurements(
        device_name: Optional[constr(strip_whitespace=True, min_length=3)] = None,
        device_token: Optional[str] = None,
        admin_token=Depends(AdminAuth())
):
    """
    List all measurements related to specific device. Pass exactly one optional field: device_name or device_token.
    """

    if (device_name is None) == (device_token is None):
        return JSONResponse({"error": 'Pass exactly one optional field: device_name or device_token.'}, 400)

    if device_name is not None:
        device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    else:
        device: Devices = db.session.query(Devices).filter(Devices.device_token == device_token).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    measurements = db.session.query(Measurements).filter(Measurements.device_id == device.device_id)
    measurements = measurements.order_by(Measurements.timestamp.asc()).all()
    if len(measurements) == 0:
        return JSONResponse({"error": 'Measurements for this device is empty'}, 400)

    timestamps = []
    temperatures = []
    humiditys = []
    for measurement in measurements:
        timestamps.append(measurement.timestamp)
        temperatures.append(measurement.temperature)
        humiditys.append(measurement.humidity)

    return {"length": len(temperatures),
            'timestamps': timestamps,
            'temperatures': temperatures,
            'humiditys': humiditys}
