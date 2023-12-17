import json
from datetime import datetime
from typing import Literal
from urllib.parse import quote

import requests
from pydantic import BaseModel

types_url = "https://api.reliefweb.int/v1/references/disaster-types"


class BaseRequestData(BaseModel):
    limit: int = 10
    appname: str


class Query(BaseModel):
    value: str
    fields: list[str] = []
    operator: Literal["AND", "OR"] = "OR"

    def to_str(self) -> str:
        query = self
        query_list = []
        query_list.append(f"query[value]={query.value}")
        for field in query.fields:
            query_list.append(f"query[fields][]={field}")
        if query.operator != "OR":
            query_list.append(f"query[operator]={query.operator}")
        return "&".join(query_list)


class Condition(BaseModel):
    field: str | None = None
    value: str | list[str] | dict[Literal["to", "from"], datetime] | None = None
    negate: bool = False
    operator: Literal["AND", "OR", None] = None

    def to_str(self, i: int | None = None) -> str:
        condition = self
        condition_list = []
        conditions_id_str = f"[conditions][{i}]" if i is not None else ""

        condition_list.append(f"filter{conditions_id_str}[field]={condition.field}")
        if isinstance(condition.value, str):
            condition_list.append(f"filter{conditions_id_str}[value]={condition.value}")
        elif isinstance(condition.value, list):
            for val in condition.value:
                condition_list.append(f"filter{conditions_id_str}[value]={val}")
            condition_list.append(
                f"filter{conditions_id_str}[operator]={condition.operator}"
            )
        elif isinstance(condition.value, dict):
            for key, val in condition.value.items():
                date_iso = (
                    val
                    # .astimezone()
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+", "%2B")
                )
                condition_list.append(
                    f"filter{conditions_id_str}[value][{key}]={date_iso}"
                )
        if condition.negate:
            condition_list.append(f"filter{conditions_id_str}[negate]=true")
        return "&".join(condition_list)


class Filter(BaseModel):
    operator: Literal["AND", "OR"] = "AND"
    conditions: list[Condition] = []

    def to_str(self) -> str:
        """
        This only works with a list of simple conditions, not with recursively nested conditions
        TODO: figure out recursively nested conditions
        """
        conditions = self
        conditions_list = []
        conditions_list.append(f"filter[operator]={conditions.operator}")
        for i, condition in enumerate(conditions.conditions):
            conditions_list.append(condition.to_str(i=i))
        return "&".join(conditions_list)


class Fields(BaseModel):
    include: list[str] = []
    exclude: list[str] = []

    def to_str(self) -> str:
        fields = self
        fields_list = []
        for field in fields.include:
            fields_list.append(f"fields[include][]={field}")
        for field in fields.exclude:
            fields_list.append(f"fields[exclude][]={field}")
        return "&".join(fields_list)


class Parameters(BaseRequestData):
    query: Query | None = None
    filter: Filter | None = None
    fields: Fields | None = None
    preset: Literal["latest", "analysis", "minimal"] = "minimal"

    def to_str(self):
        parameters = self
        parameters_list = []
        parameters_list.append(
            f"appname={parameters.appname}&limit={parameters.limit}&preset={parameters.preset}"
        )

        if parameters.query:
            parameters_list.append(parameters.query.to_str())
        if parameters.filter:
            if len(parameters.filter.conditions) == 1:
                parameters_list.append(parameters.filter.conditions[0].to_str())
            else:
                parameters_list.append(parameters.filter.to_str())
        if parameters.fields:
            parameters_list.append(parameters.fields.to_str())
        return "&".join(parameters_list)
