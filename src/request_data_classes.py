import json
from datetime import datetime
from typing import Literal
from urllib.parse import quote

import requests
from pydantic import BaseModel

types_url = "https://api.reliefweb.int/v1/references/disaster-types"


class BaseRequestData(BaseModel):
    limit: int = 10
    appname: str = ""


class Query(BaseRequestData):
    value: str | None = None
    fields: list[str] = []
    operator: Literal["AND", "OR"] = "OR"


class Condition(BaseRequestData):
    field: str | None = None
    value: str | list[str] | dict[Literal["to", "from"], str | datetime] | None = None
    negate: bool = False
    operator: Literal["AND", "OR"] = "OR"


class Conditions(Condition):
    operator: Literal["AND", "OR"] = "AND"
    conditions: list[Condition] = []


class Fields(BaseRequestData):
    include: list[str] = []
    exclude: list[str] = []


class RequestData(BaseRequestData):
    query: Query | None = None
    filter: Conditions | None = None
    fields: Fields | None = None
