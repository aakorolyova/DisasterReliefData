from datetime import datetime, timezone

import requests

from request_data_classes import (
    Condition,
    DisasterType,
    Fields,
    Filter,
    Parameters,
    PrimaryCountry,
    PrimaryDisasterType,
    Query,
)


def monitor():
    appname = "omdena-datacamp"
    url_reports = "https://api.reliefweb.int/v1/reports?"
    url_disasters = "https://api.reliefweb.int/v1/disasters?"

    conditions = Filter(
        conditions=[
            PrimaryCountry(value="United States of America"),
            Condition(
                field="date.created",
                value={
                    "from": datetime.now(tz=timezone.utc),
                },
            ),
        ],
    )

    fields_to_include_reports = Fields(
        include=["body", "primary_country", "date", "disaster_type"],
    )
    fields_to_include_disasters = Fields(
        include=["primary_country", "date", "primary_type"],
    )

    parameters_reports = Parameters(
        appname=appname,
        filter=conditions,
        fields=fields_to_include_reports,
        limit=100,
    )
    parameters_disasers = Parameters(
        appname=appname,
        filter=conditions,
        fields=fields_to_include_disasters,
        limit=100,
    )

    response_reports = requests.get(url=url_reports + parameters_reports.to_str())
    response_disasters = requests.get(url=url_disasters + parameters_disasers.to_str())

    print(response_reports.status_code)
    print(response_disasters.status_code)

    date = datetime.now().strftime("%m-%d_%H-%M")
    if response_reports.json().get("count") or response_disasters.json.get("count"):
        res = "Warning! Something ia happening in the US"
    else:
        res = "Everything is ok"

    with open(f"monitoring_logs/{date}.txt", "w") as f:
        f.write(res)


if __name__ == "__main__":
    monitor()
