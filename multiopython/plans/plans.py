from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, validate_call
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated

from .actions import ACTIONS, Action, Sink
from .utils import make_validator


def convert_to_actions(
    v: Any,
) -> Action:
    if not isinstance(v, (Action, dict)):
        raise ValueError(f"Action must be a dict or an instance of Action, not {type(v)}")
    if isinstance(v, Action):
        return v
    if "type" not in v:
        raise ValueError("Action must have a type")
    if v["type"] not in ACTIONS:
        raise ValueError(f"Invalid action type, should be one of {list(ACTIONS.keys())}")
    action = ACTIONS[v["type"]](**v)
    return action


Actions = Annotated[dict | Action, WrapValidator(make_validator(convert_to_actions))]
Name = Annotated[str, lambda x: x.replace(" ", "-")]


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
        [], title="Actions", description="List of actions to be performed", validate_default=True
    )

    @field_validator("actions")
    @classmethod
    def __check_has_sink(cls, v):
        if len(v) == 0:
            return [Sink()]
        contains_sink = False
        for action in v:
            if isinstance(action, Sink):
                contains_sink = True
                break
        if not contains_sink:
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

    plans: list[Plan] = Field([], title="Plans", description="List of plans to be executed")

    @validate_call
    def add_plan(self, plan: Plan):
        self.plans.append(plan)

    @validate_call
    def extend_plans(self, plans: list[Plan]):
        self.plans.extend(plans)


__all__ = ["Config", "Plan"]
