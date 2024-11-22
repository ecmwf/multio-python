# (C) Copyright 2024 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from __future__ import annotations

import os
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, model_serializer, model_validator, validate_call
from typing_extensions import Annotated

from .actions import ACTIONS, SingleField, Sink, Transport

Name = Annotated[str, lambda x: x.replace(" ", "-")]
Actions = Annotated[ACTIONS, Field(discriminator="type", title="Actions")]


class MultioBaseModel(BaseModel):
    """Multio Base Model"""

    model_config = ConfigDict(
        extra="forbid",
    )

    @classmethod
    def from_yamlfile(cls, file: str):
        """
        Create a model from a YAML file
        """
        return cls.from_yaml(open(file))

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """
        Create a model from a YAML string
        """
        import yaml

        return cls.model_validate(yaml.safe_load(yaml_str), strict=True)

    @validate_call
    def write(self, file: os.PathLike, *, format: Literal["yaml", "json"] = "yaml") -> None:
        """
        Write the model to a file

        Parameters
        ----------
        file : os.PathLike
            Path to write to
        format : Literal['yaml', 'json']
            Package to use for dumping, defaults to 'yaml'.
        """
        if format == "yaml":
            import yaml

            method = yaml.safe_dump
        elif format == "json":
            import json

            method = json.dump

        with open(file, "w") as f:
            method(self.dump(), f)

    def dump(self) -> dict:
        """
        Dump the model to a python dict
        """
        return self.model_dump(serialize_as_any=True)

    def dump_json(self) -> str:
        """
        Dump the model to a JSON string
        """
        import json

        return json.dumps(self.dump())

    def dump_yaml(self) -> str:
        """
        Dump the model to a yaml string
        """
        import yaml

        return yaml.safe_dump(self.dump(), sort_keys=False)


class Plan(MultioBaseModel):
    """
    Multio Plan

    Multio requires a valid plan to contain at least one Sink.

    Examples:
    ```python
        plan = Plan(name="Plan1", action = [{"type": "print"}])
        plan.add_action({"type": "print"})
        plan.add_action({"type": "select", "match": [{"key": "value"}]})
        plan.add_action({"type": "sink", "sinks": [{"type": "file", "path": "output.txt"}]})
    ```

    """

    name: Name = Field(title="Name", description="Name of the plan")
    actions: list[Actions] = Field(
        default_factory=lambda: [],
        title="Actions",
        description="List of actions to be performed",
        validate_default=True,
    )

    @validate_call
    def add_action(self, action: Actions):
        self.actions.append(action)

    @validate_call
    def extend_actions(self, actions: list[Actions]):
        self.actions.extend(actions)

    def check_validity(self) -> bool:
        """Check if the plan is valid"""
        if not any([isinstance(action, (Transport, Sink, SingleField)) for action in self.actions]):
            return False
        return True

    def ensure_sink(self) -> "Plan":
        """Ensure that the plan has at least one Sink"""
        if not any([isinstance(action, Sink) for action in self.actions]):
            self.add_action(Sink())
        return self

    def to_client(self) -> CONFIGS:
        return Client(plans=[self])

    def to_server(self) -> CONFIGS:
        return Server(plans=[self])

    def __add__(self, other) -> CONFIGS:
        if not isinstance(other, Plan):
            return NotImplemented
        return Client(plans=[self, other])


def discriminate_config(v: dict) -> Literal["Client", "Server"]:
    """
    Discriminate the config based on the presence of the transport key
    """
    if "transport" in v:
        return "Server"
    return "Client"


class BaseConfig(MultioBaseModel):
    """
    Multio BaseConfig.

    Examples:
    ```python
        config = Config()
        plan = Plan(name="Plan1", plans = [{"type": "print"}])
        plan.add_action({"type": "print"})
        plan.add_action({"type": "select", "match": [{"key": "value"}]})
        plan.add_action({"type": "sink", "sinks": [{"type": "file", "path": "output.txt", "append": False}]})
        config.add_plan(plan)
    ```
    """

    plans: list[Plan] = Field(title="Plans", description="List of plans to be executed")

    @validate_call
    def add_plan(self, plan: Plan):
        self.plans.append(plan)

    @validate_call
    def extend_plans(self, plans: list[Plan]):
        self.plans.extend(plans)


class Client(BaseConfig):
    """Client Config"""

    def to_server(self) -> CONFIGS:
        return Server(plans=[self.plans])


class Server(BaseConfig):
    """
    Server Config.

    Adds transport protocol to the Config
    """

    transport: Optional[str] = Field(None, title="Transport", description="Transport protocol to use")
    group: Optional[str] = None
    count: Optional[int] = None


CONFIGS = Annotated[
    Union[Annotated[Client, Tag("Client")], Annotated[Server, Tag("Server")]], Discriminator(discriminate_config)
]


class Collection(MultioBaseModel):
    """
    Multio Collection of Configs
    """

    configs: dict[str, CONFIGS] = Field(default_factory=dict, title="Configs", description="Collection of Configs")

    @validate_call
    def add_config(self, key: str, config: CONFIGS):
        self.configs[key] = config

    @validate_call
    def __get__(self, key: str) -> CONFIGS:
        return self.configs[key]

    @validate_call
    def __set__(self, key: str, config: CONFIGS):
        self.configs[key] = config

    @model_validator(mode="before")
    @classmethod
    def __convert_to_pydantic(cls, data: Any) -> dict:
        return {"configs": data}

    @model_serializer
    def __convert_to_multio(self) -> dict[str, Any]:
        return {k: v.dump() for k, v in self.configs.items()}


__all__ = ["Client", "Server", "Plan", "Collection"]
