import json
from datetime import datetime
from typing import Literal
from urllib.parse import quote

import requests
from pydantic import BaseModel, ValidationError, validator

from utils import get_country_list, get_disaster_types

disaster_types = get_disaster_types()
country_list = get_country_list()


class BaseRequestData(BaseModel):
    limit: int = 10
    appname: str = "omdena-datacamp"
    preset: Literal["latest", "analysis", "minimal"] = "minimal"


class Query(BaseRequestData):
    value: str
    fields: list[str] = []
    operator: Literal["AND", "OR"] = "OR"

    def to_str(self, include_base_params: bool = True) -> str:
        param_list = []
        if include_base_params:
            param_list.append(
                f"appname={self.appname}&limit={self.limit}&preset={self.preset}"
            )
        param_list.append(f"query[value]={self.value}")
        for field in self.fields:
            param_list.append(f"query[fields][]={field}")
        if self.operator != "OR":
            param_list.append(f"query[operator]={self.operator}")
        return "&".join(param_list)


class Condition(BaseRequestData):
    field: str | None = None
    value: str | list[str] | dict[Literal["to", "from"], datetime] | None = None
    negate: bool = False
    operator: Literal["AND", "OR", None] = None

    def to_str(self, i: int | None = None, include_base_params: bool = True) -> str:
        param_list = []
        if include_base_params:
            param_list.append(
                f"appname={self.appname}&limit={self.limit}&preset={self.preset}"
            )
        conditions_id_str = f"[conditions][{i}]" if i is not None else ""

        param_list.append(f"filter{conditions_id_str}[field]={self.field}")
        if isinstance(self.value, str):
            param_list.append(f"filter{conditions_id_str}[value]={self.value}")
        elif isinstance(self.value, list):
            for val in self.value:
                param_list.append(f"filter{conditions_id_str}[value]={val}")
            param_list.append(f"filter{conditions_id_str}[operator]={self.operator}")
        elif isinstance(self.value, dict):
            for key, val in self.value.items():
                date_iso = (
                    val
                    # .astimezone()
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+", "%2B")
                )
                param_list.append(f"filter{conditions_id_str}[value][{key}]={date_iso}")
        if self.negate:
            param_list.append(f"filter{conditions_id_str}[negate]=true")
        return "&".join(param_list)


class PrimaryCountry(Condition):
    field: str = "primary_country"
    value: str | list[str] | None = None

    @validator("value")
    def validate_country_name(cls, v):
        if isinstance(v, str):
            if v not in country_list:
                raise ValueError(
                    f"Country name {v} not in the list of allowed country names"
                )
        elif isinstance(v, list):
            for s in v:
                if s not in country_list:
                    raise ValueError(
                        f"Country name {s} not in the list of allowed country names"
                    )
        return v


class DisasterType(Condition):
    """
    Disaster type filter to be used with reports endpoint
    """

    field: str = "disaster_type"
    value: str | list[str] | None = None

    @validator("value")
    def validate_disaster_type(cls, v):
        if isinstance(v, str):
            if v not in disaster_types:
                raise ValueError(
                    f"Disaster type {v} not in the list of allowed disaster types"
                )
        elif isinstance(v, list):
            for s in v:
                if s not in disaster_types:
                    raise ValueError(
                        f"Disaster type {s} not in the list of allowed disaster types"
                    )
        return v


class PrimaryDisasterType(DisasterType):
    """
    Disaster type filter to be used with disasters endpoint
    """

    field: str = "primary_type"


class Filter(BaseRequestData):
    operator: Literal["AND", "OR"] = "AND"
    conditions: list[Condition] = []

    def to_str(self, include_base_params: bool = True) -> str:
        """
        This only works with a list of simple conditions, not with recursively nested conditions
        TODO: figure out recursively nested conditions
        """
        param_list = []
        if include_base_params:
            param_list.append(
                f"appname={self.appname}&limit={self.limit}&preset={self.preset}"
            )
        param_list.append(f"filter[operator]={self.operator}")
        for i, condition in enumerate(self.conditions):
            param_list.append(condition.to_str(i=i))
        return "&".join(param_list)


class Fields(BaseRequestData):
    include: list[str] = []
    exclude: list[str] = []

    def to_str(self, include_base_params: bool = True) -> str:
        param_list = []
        if include_base_params:
            param_list.append(
                f"appname={self.appname}&limit={self.limit}&preset={self.preset}"
            )
        for field in self.include:
            param_list.append(f"fields[include][]={field}")
        for field in self.exclude:
            param_list.append(f"fields[exclude][]={field}")
        return "&".join(param_list)


class Parameters(BaseRequestData):
    query: Query | None = None
    filter: Filter | None = None
    fields: Fields | None = None

    def to_str(self):
        param_list = []
        param_list.append(
            f"appname={self.appname}&limit={self.limit}&preset={self.preset}"
        )

        if self.query:
            param_list.append(self.query.to_str(include_base_params=False))
        if self.filter:
            if len(self.filter.conditions) == 1:
                param_list.append(
                    self.filter.conditions[0].to_str(include_base_params=False)
                )
            else:
                param_list.append(self.filter.to_str(include_base_params=False))
        if self.fields:
            param_list.append(self.fields.to_str(include_base_params=False))
        return "&".join(param_list)
