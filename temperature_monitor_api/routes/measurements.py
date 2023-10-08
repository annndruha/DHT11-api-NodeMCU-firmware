import math
import logging
import datetime
from typing import Optional

from pydantic import constr
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from fastapi.responses import JSONResponse
from sqlalchemy.sql import func

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Devices, Measurements
from temperature_monitor_api.utils.utils import object_as_dict
from temperature_monitor_api.routes.auth import AdminAuth
from temperature_monitor_api.routes.schemas import SuccessResponseSchema, ErrorResponseSchema, ForbiddenSchema, \
    MeasurementSchema, ListMeasurementsSchema, ListMeasurementsChatJsSchema

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

    Warning: if measurement same as last measurement for device, it skips for save disk space reason.
    But if last measurement older than 1 minute, it writes anyway.
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

    db.session.add(Measurements(device_id=device.device_id,
                                temperature=temperature,
                                humidity=humidity))
    db.session.flush()
    db.session.commit()
    return {"detail": 'Added'}


@router.get('/measurements',
            responses={200: {"model": ListMeasurementsSchema},
                       400: {"model": ErrorResponseSchema},
                       403: {"model": ForbiddenSchema}})
async def list_measurements_plain(
        device_name: constr(strip_whitespace=True, min_length=3),
        limit: Optional[int] = None,
        only_last_24_hours: Optional[bool] = True
):
    """
    List measurements related to specific device in plain format.

    Sorted by ascending timestamp, but limit calculate reversed from last measurement.
    """
    if device_name is None:
        return JSONResponse({"error": 'Field device_name is required'}, 400)

    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    measurements = db.session.query(Measurements).filter(Measurements.device_id == device.device_id)
    measurements = measurements.order_by(Measurements.timestamp.desc())

    if only_last_24_hours:
        shift = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))) - datetime.timedelta(days=1)
        measurements = measurements.filter(Measurements.timestamp > shift)

    if limit:
        measurements = measurements.limit(limit)

    measurements = measurements.all()
    if len(measurements) == 0:
        return JSONResponse({"error": 'Measurements for this device is empty'}, 400)

    timestamps = []
    temperatures = []
    humiditys = []
    for measurement in reversed(measurements):
        timestamps.append(measurement.timestamp)
        temperatures.append(measurement.temperature)
        humiditys.append(measurement.humidity)

    return {"length": len(temperatures),
            'timestamps': timestamps,
            'temperatures': temperatures,
            'humiditys': humiditys}


@router.get('/measurements_chart_js',
            responses={200: {"model": ListMeasurementsChatJsSchema},
                       400: {"model": ErrorResponseSchema},
                       403: {"model": ForbiddenSchema}})
async def list_measurements_in_chart_js_format(
        device_name: constr(strip_whitespace=True, min_length=3),
        limit: Optional[int] = None,
        only_last_24_hours: Optional[bool] = True
):
    """
    List measurements related to specific device in Chart.js format.

    Sorted by ascending timestamp, but limit calculate reversed from last measurement.

    Point returned in specific format for chart.js performance: same points ignores, bat if value changes,
    duplicate are spawn with same as previous datetime (For disable line not parallel with X/Y)
    """
    if device_name is None:
        return JSONResponse({"error": 'Field device_name is required'}, 400)

    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    measurements = db.session.query(Measurements).filter(Measurements.device_id == device.device_id)
    measurements = measurements.order_by(Measurements.timestamp.desc())

    if only_last_24_hours:
        shift = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))) - datetime.timedelta(days=1)
        measurements = measurements.filter(Measurements.timestamp > shift)

    if limit:
        measurements = measurements.limit(limit)

    measurements = measurements.all()
    if len(measurements) == 0:
        return JSONResponse({"error": 'Measurements for this device is empty'}, 400)

    res = {"temperatures": [], "humiditys": []}
    prev_point = measurements[-1]

    def append_point(res, measurement):
        datetime_str = (datetime.datetime.strptime(str(measurement.timestamp), '%Y-%m-%d %H:%M:%S.%f') +
                        datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        temp_item = {'x': datetime_str,
                     'y': measurement.temperature}
        hum_item = {'x': datetime_str,
                    'y': measurement.humidity}
        res["temperatures"].append(temp_item)
        res["humiditys"].append(hum_item)

    for measurement in reversed(measurements):
        if measurement.temperature != prev_point.temperature or measurement.humidity != prev_point.humidity:
            prev_point.timestamp = measurement.timestamp
            append_point(res, prev_point)
            append_point(res, measurement)
            prev_point = measurement
    return res
