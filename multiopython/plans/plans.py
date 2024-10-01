from typing import Any, Union

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
    @classmethod
    def from_yamlfile(cls, file):
        return cls.from_yaml(open(file))

    @classmethod
    def from_yaml(cls, yaml_str):
        import yaml

        return cls.model_validate(yaml.safe_load(yaml_str))

    def write(self, file):
        with open(file, "w") as f:
            f.write(self.dump())

    def dump(self):
        return self.model_dump(mode="json", serialize_as_any=True)


class Plan(MultioBaseModel):
    name: Name = Field(title="Name", description="Name of the plan")
    actions: list[Actions] = Field(title="Actions", description="List of actions to be performed")

    @validate_call
    def add_action(self, action: Actions):
        self.actions.append(action)

    @validate_call
    def extend_actions(self, actions: list[Actions]):
        self.actions.extend(actions)


class Config(MultioBaseModel):
    plans: list[Plan] = Field(title="Plans", description="List of plans to be executed")

    def add_plan(self, plan: Plan):
        self.plans.append(plan)

    def extend_plans(self, plans: list[Plan]):
        self.plans.extend(plans)


__all__ = ["Config", "Plan"]
