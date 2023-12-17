# %%
import json
from datetime import datetime, timezone

import requests

from request_data_classes import Condition, Fields, Filter, Parameters, Query

# %%
appname = "omdena-datacamp"
url_reports = "https://api.reliefweb.int/v1/reports?"
url_disasters = "https://api.reliefweb.int/v1/disasters?"

# %%
condition = Condition(
    field="country",
    value="Türkiye",
)

# %%
conditions = Filter(
    conditions=[
        Condition(field="primary_country", value="Türkiye"),
        Condition(
            field="date.created",
            value={
                "from": datetime(year=2023, month=2, day=5, tzinfo=timezone.utc),
                "to": datetime(year=2023, month=10, day=5, tzinfo=timezone.utc),
            },
        ),
        Condition(field="disaster_type", value="earthquake"),
    ],
)

# %%
query = Query(
    value="Gaziantep",
)

# %%
fields_to_include = Fields(
    include=["body", "primary_country", "date", "disaster_type"],
)

# %%
parameters = Parameters(
    query=query,
    appname=appname,
    filter=conditions,
    fields=fields_to_include,
    limit=1000,
)

# %%
params = parameters
print(url_reports + params.to_str())
response = requests.get(url=url_reports + params.to_str())
print(response.status_code)
print(response.json())

# %%
with open("data/Turkey.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=1)

# %%
for params in [query, fields_to_include, condition, conditions, parameters]:
    print(params.to_str())
    response = requests.get(url=url_reports + params.to_str())
    print(response.status_code)
    print(response.json())
    print()
