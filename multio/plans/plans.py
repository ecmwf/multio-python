# (C) Copyright 2024 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from __future__ import annotations

import os
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, validate_call
from typing_extensions import Annotated

from .actions import ACTIONS, Sink

Name = Annotated[str, lambda x: x.replace(" ", "-")]
Actions = Annotated[ACTIONS, Field(discriminator="type", alias="actions", title="Actions")]


class MultioBaseModel(BaseModel):
    """Multio Base Model"""

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

        return cls.model_validate(yaml.safe_load(yaml_str))

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

        return yaml.safe_dump(self.dump())


class Plan(MultioBaseModel):
    """
    Multio Plan

    Multio requires a valid plan to contain at least one Sink.
    So if none provided by the user, an empty one will be auto appended.

    Examples:
    ```python
        plan = Plan(name="Plan1")
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

    @field_validator("actions")
    @classmethod
    def __check_has_sink(cls, v):
        """Force actions to contain at least one Sink

        As Multio requires a valid plan to contain at least one Sink,
        """
        if len(v) == 0:
            return [Sink()]
        if not any([isinstance(action, Sink) for action in v]):
            v.append(Sink())
        return v

    @validate_call
    def add_action(self, action: Actions):
        self.actions.append(action)

    @validate_call
    def extend_actions(self, actions: list[Actions]):
        self.actions.extend(actions)

    def to_config(self) -> Config:
        return Config(plans=[self])

    def __add__(self, other) -> Config:
        if not isinstance(other, Plan):
            return NotImplemented
        return Config(plans=[self, other])


class Config(MultioBaseModel):
    """
    Multio Config

    Examples:
    ```python
        config = Config()
        plan = Plan(name="Plan1")
        plan.add_action({"type": "print"})
        plan.add_action({"type": "select", "match": [{"key": "value"}]})
        plan.add_action({"type": "sink", "sinks": [{"type": "file", "path": "output.txt", "append": False}]})
        config.add_plan(plan)
    ```
    """

    plans: list[Plan] = Field(default_factory=lambda: [], title="Plans", description="List of plans to be executed")
    transport: Optional[str] = Field(None, title="Transport", description="Transport protocol to use")
    group: Optional[str] = None
    count: Optional[int] = None

    @validate_call
    def add_plan(self, plan: Plan):
        self.plans.append(plan)

    @validate_call
    def extend_plans(self, plans: list[Plan]):
        self.plans.extend(plans)


__all__ = ["Config", "Plan"]
