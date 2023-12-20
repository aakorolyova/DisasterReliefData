import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import quote

import requests
from gdacs.api import GDACSAPIReader


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


def get_local_current_event_gdacs(
    client: GDACSAPIReader,
    country: str,
    time_delta: timedelta,
    date: datetime = datetime.now(),
    event_type: str | None = None,
    limit=100,
):
    events = client.latest_events(event_type=event_type, limit=limit)  # type: ignore
    relevant_timespan = date - time_delta
    relevant = []
    for event in events.features:
        properties = event.get("properties", {})
        affected_countries = [
            c.get("countryname") for c in properties.get("affectedcountries", []) if c
        ]
        affected_countries_iso3 = [
            c.get("iso3") for c in properties.get("affectedcountries", []) if c
        ]
        if country in affected_countries + affected_countries_iso3:
            start_date_str = properties.get("fromdate", "")
            end_date_str = properties.get("todate", "")

            start_date = (
                datetime.fromisoformat(start_date_str) if start_date_str else None
            )
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
            if (start_date and start_date > relevant_timespan) or (
                end_date and end_date > relevant_timespan
            ):
                relevant.append(event)
    return relevant
