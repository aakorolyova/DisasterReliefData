import json
from datetime import datetime
from typing import Literal
from urllib.parse import quote

import requests

from request_data_classes import (
    BaseRequestData,
    Condition,
    Fields,
    Filter,
    Parameters,
    Query,
)


def get_disaster_types(
    types_url="https://api.reliefweb.int/v1/references/disaster-types",
):
    response = requests.get(types_url)
    data = response.json()["data"]
    disaster_id2type = {
        item.get("id", None): item.get("fields", {}).get("name", None) for item in data
    }
    disaster_type2id = {
        item.get("fields", {}).get("name", None): item.get("id", None) for item in data
    }
    return disaster_id2type, disaster_type2id


def request_with_params(
    url, params: BaseRequestData | Query | Condition | Filter | Fields
):
    response = requests.get(
        url, params=params.model_dump(exclude_none=True, exclude_unset=True)
    )
    return response.status_code, response.json()
