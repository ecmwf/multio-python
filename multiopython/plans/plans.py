from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, Field, validate_call
from pydantic.functional_validators import WrapValidator
from typing_extensions import Annotated

from .actions import ACTIONS, Action
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
    def from_yamlfile(cls, file):
        """
        Create a model from a YAML file
        """
        return cls.from_yaml(open(file))

    @classmethod
    def from_yaml(cls, yaml_str):
        """
        Create a model from a YAML string
        """
        import yaml

        return cls.model_validate(yaml.safe_load(yaml_str))

    def write(self, file):
        """
        Write the model to a file
        """
        with open(file, "w") as f:
            f.write(self.dump())

    def dump(self):
        """
        Dump the model to a json string
        """
        return self.model_dump(mode="json", serialize_as_any=True)


class Plan(MultioBaseModel):
    """
    Multio Plan

    Examples:
    ```python
        plan = Plan(name="Plan1")
        plan.add_action({"type": "print"})
        plan.add_action({"type": "select", "match": [{"key": "value"}]})
        plan.add_action({"type": "sink", "sinks": [{"type": "file", "path": "output.txt"}]})
    ```

    """

    name: Name = Field(title="Name", description="Name of the plan")
    actions: list[Actions] = Field([], title="Actions", description="List of actions to be performed")

    @validate_call
    def add_action(self, action: Actions):
        self.actions.append(action)

    @validate_call
    def extend_actions(self, actions: list[Actions]):
        self.actions.extend(actions)

    def to_config(self) -> Config:
        return Config(plans=[self])

    def __add__(self, other: Self) -> Self:
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
