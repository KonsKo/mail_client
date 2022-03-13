"""
Config module.

Module describe structure of application config.
"""

from pydantic import BaseModel
from typing import Optional


class BodyDelete(BaseModel):
    filter_set: Optional[dict]


class BodyCreate(BaseModel):
    """Body structure for inserting data."""

    payload: dict


class BodyUpdate(BaseModel):
    """Body structure for updating data."""

    payload: dict
    filter_set: Optional[dict]


class POSTBody(BaseModel):
    filter_set: Optional[dict]
    payload: Optional[dict]
