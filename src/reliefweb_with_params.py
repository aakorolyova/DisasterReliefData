import json
from datetime import datetime
from typing import Literal
from urllib.parse import quote

import requests
from pydantic import BaseModel

from request_data_classes import (
    BaseRequestData,
    Condition,
    Conditions,
    Fields,
    Query,
    RequestData,
)
from utils import request_with_data, request_with_params

appname = "omdena-datacamp"
url_reports = "https://api.reliefweb.int/v1/reports?"
url_disasters = "https://api.reliefweb.int/v1/disasters?"

condition = Condition(
    field="primary_country",
    value="Turkey",
    appname=appname,
)
conditions = Conditions(
    conditions=[
        Condition(field="primary_country", value="Turkey"),
        Condition(
            field="date.created",
            value={
                "from": datetime(year=2023, month=2, day=5),
                "to": datetime(year=2023, month=4, day=5),
            },
        ),
        Condition(field="disaster_type", value="earthquake"),
    ],
    appname=appname,
)
query = Query(
    value="Gaziantep",
    appname=appname,
)
fields_to_include = Fields(
    include=["body", "primary_country", "date", "disaster_type"],
    appname=appname,
)
parameters = RequestData(
    query=query,
    appname=appname,
    filter=conditions,
    fields=fields_to_include,
    limit=1000,
)

for params in [condition, conditions, query, fields_to_include]:
    status_code, response = request_with_params(url=url_reports, params=params)
    print(status_code)


status_code, response = request_with_data(url=url_reports, data=parameters)
print(status_code)


# with open("data/Turkey.json", "w", encoding="utf-8") as f:
#     json.dump(response.json(), f, indent=1)
