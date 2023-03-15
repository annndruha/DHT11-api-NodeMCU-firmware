import logging
import time
from typing import List, Optional

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from pydantic import constr
from sqlalchemy import and_, func, or_

from temperature_monitor_api.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

test_measurements = []


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

    if len(test_measurements) > 0:
        return {"success": True,
                "measurements": test_measurements}
    else:
        return {"success": False}


@router.post('/measurements')
def set_measurements(
        access_token: constr(strip_whitespace=True, to_upper=True, min_length=1),
        temperature: float,
        humidity: float
):
    if access_token != settings.ACCESS_TOKEN:
        raise HTTPException(401, 'Unauthorized. Given access_token not accepted')

    test_measurements.append((time.time(),
                              temperature,
                              humidity))
    return {"success": True}

# endregion
