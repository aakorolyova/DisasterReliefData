import json
from datetime import datetime
from pathlib import Path
from typing import Literal
from urllib.parse import quote

import requests


def get_disaster_types(
    url="https://api.reliefweb.int/v1/references/disaster-types",
    path=Path("data/disaster_types.json"),
):
    if path.exists():
        with open(path, "r") as f:
            response = json.load(f)
    else:
        response = requests.get(url).json()
        with open(path, "w") as f:
            json.dump(response, f)
    data = response["data"]
    disaster_id2type = {
        item.get("id", None): item.get("fields", {}).get("name", None) for item in data
    }
    disaster_type2id = {
        item.get("fields", {}).get("name", None): item.get("id", None) for item in data
    }
    return disaster_id2type, disaster_type2id


def get_country_list(
    url="https://api.reliefweb.int/v1/countries?appname=rwint-user-0&profile=list&preset=latest&slim=1&limit=1000",
    path=Path("data/country_list.json"),
) -> list[str]:
    if path.exists():
        with open(path, "r") as f:
            response = json.load(f)
    else:
        response = requests.get(url).json()
        with open(path, "w") as f:
            json.dump(response, f)
    data = response["data"]
    names = [
        item.get("fields", {}).get("name")
        for item in data
        if item.get("fields", {}).get("name")
    ]
    return names
