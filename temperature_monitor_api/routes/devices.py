import logging
from typing import Optional

from pydantic import constr
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from fastapi.responses import JSONResponse

from temperature_monitor_api.settings import get_settings
from temperature_monitor_api.models.base import Devices, Measurements
from temperature_monitor_api.utils.utils import object_as_dict, generate_serial_number
from temperature_monitor_api.routes.auth import AdminAuth
from temperature_monitor_api.routes.schemas import SuccessResponseSchema, ErrorResponseSchema, ForbiddenSchema, \
    DeviceSchema, ListDevicesSchema

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post('/create_device', responses={200: {"model": DeviceSchema},
                                          400: {"model": ErrorResponseSchema},
                                          403: {"model": ForbiddenSchema}})
async def create_new_device(
        device_name: constr(strip_whitespace=True, min_length=3),
        device_predefined_token: Optional[str] = None,
        admin_token=Depends(AdminAuth())
):
    """
    Create a new device
    """
    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if device:
        return JSONResponse({"error": 'Device name already taken'}, 400)

    device_token = generate_serial_number() if device_predefined_token is None else device_predefined_token

    db.session.add(Devices(device_name=device_name, device_token=device_token))
    db.session.flush()
    db.session.commit()

    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    return object_as_dict(device)


@router.get('/get_device', responses={200: {"model": DeviceSchema},
                                      400: {"model": ErrorResponseSchema},
                                      403: {"model": ForbiddenSchema}})
async def get_specific_device(
        device_name: constr(strip_whitespace=True, min_length=3),
        admin_token=Depends(AdminAuth())
):
    """
    Get a specific device info
    """
    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    return object_as_dict(device)


@router.get('/list_devices', responses={200: {"model": ListDevicesSchema},
                                        400: {"model": ErrorResponseSchema},
                                        403: {"model": ForbiddenSchema}})
async def list_all_devices(
        admin_token=Depends(AdminAuth())
):
    """
    Get a list of devices with name's, id's, tokens, creation date's
    """
    devices: Devices = db.session.query(Devices)
    devices_list = [object_as_dict(device) for device in devices.all()]

    if not len(devices_list):
        return JSONResponse({"error": 'No in device found'}, 400)

    return {"devices": devices_list}


@router.patch('/update_device', responses={200: {"model": DeviceSchema},
                                           400: {"model": ErrorResponseSchema},
                                           403: {"model": ForbiddenSchema}})
async def update_specific_device(
        device_name: constr(strip_whitespace=True, min_length=3),
        new_device_name: Optional[constr(strip_whitespace=True, min_length=3)] = None,
        new_device_token: Optional[str] = None,
        admin_token=Depends(AdminAuth())
):
    """
    Update device name and/or device token
    """
    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    if new_device_name is None and new_device_token is None:
        return JSONResponse({"error": 'Not passed any update fields. Nothing to update.'}, 400)

    if new_device_name is not None:
        device.device_name = new_device_name
        db.session.flush()
        db.session.commit()

    if new_device_token is not None:
        device.device_token = new_device_token
        db.session.flush()
        db.session.commit()

    return object_as_dict(device)


@router.delete('/delete_device', responses={200: {"model": SuccessResponseSchema},
                                            400: {"model": ErrorResponseSchema},
                                            403: {"model": ForbiddenSchema}})
async def delete_specific_device(
        device_name: constr(strip_whitespace=True, min_length=3),
        admin_token=Depends(AdminAuth())
):
    """
    Delete specific device and related measurements
    """
    device: Devices = db.session.query(Devices).filter(Devices.device_name == device_name).one_or_none()
    if not device:
        return JSONResponse({"error": 'Device with this name not existed'}, 400)

    measurements: Measurements = db.session.query(Measurements).filter(Measurements.device_id == device.device_id)
    measurements.delete()
    db.session.flush()
    db.session.commit()

    db.session.delete(device)
    db.session.flush()
    db.session.commit()

    return {"detail": f'Device {device.device_name} deleted.'}
