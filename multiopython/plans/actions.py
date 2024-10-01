from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationInfo, WrapValidator, field_validator, validate_call
from typing_extensions import Annotated

from .sinks import SINKS, Sinks
from .utils import make_validator


def convert_to_sinks(v: Any) -> Sinks:
    """
    Convert a general dict to a Sinks instance
    """
    if not isinstance(v, (Sinks, dict)):
        raise ValueError(f"Sinks must be a dict or an instance of Sinks, not {type(v)}")
    if isinstance(v, Sinks):
        return v
    if "type" not in v:
        raise ValueError("Sinks must have a type")
    if v["type"] not in SINKS:
        raise ValueError(f"Invalid sink type, must be one of {list(SINKS.keys())}")
    sink = SINKS[v["type"]](**v)
    return sink


SinkType = Annotated[dict | Sinks, WrapValidator(make_validator(convert_to_sinks))]


class Action(BaseModel):
    """Base Action class"""

    type: str


class Select(Action):
    """Select Action"""

    type: Literal["select"] = "select"
    match: list[dict[str, Any]]


class Statistics(Action):
    """Statistics Action"""

    type: Literal["statistics"] = "statistics"
    operations: list[Literal["average", "minimum", "maximum", "accumulate", "instant"]]
    output_frequency: str = Field(serialization_alias="output-frequency", examples=["5h", "10d", "1w"])


class Transport(Action):
    """Transport Action"""

    type: Literal["transport"] = "transport"
    target: str


class Aggregation(Action):
    """Aggregation Action"""

    type: Literal["aggregation"] = "aggregation"


class Print(Action):
    """Print Action"""

    type: Literal["print"] = "print"
    stream: Literal["cout"] = Field("cout")
    prefix: str = Field("")


class Mask(Action):
    """Mask Action"""

    type: Literal["mask"] = "mask"


def force_on_grib(v: str, info: ValidationInfo) -> str:
    """Force template and grid_type on grib format"""
    if info.format == "grib":
        if v is None:
            raise ValueError("template & grid_type is required for grib format")
    return v


class Encode(Action):
    """Encode Action"""

    type: Literal["encode"] = "encode"
    format: Literal["grib", "raw"]
    template: str | None = Field(None, validate_default=True)
    grid_type: str | None = Field(None, serialization_alias="grid-type")

    @field_validator("template", "grid_type", mode="after")
    @classmethod
    def check_not_none(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("format") == "grib" and v is None:
            raise ValueError("template & grid_type is required for grib format")
        return v


class Sink(Action):
    """Sink Action"""

    type: Literal["sink"] = "sink"
    sinks: list[SinkType]

    @validate_call
    def add_sink(self, sink: SinkType):
        self.sinks.append(sink)


ACTIONS = {
    "select": Select,
    "statistics": Statistics,
    "transport": Transport,
    "aggregation": Aggregation,
    "mask": Mask,
    "encode": Encode,
    "sink": Sink,
    "print": Print,
}

__all__ = ["ACTIONS", "Action", "Select", "Statistics", "Transport", "Aggregation", "Print", "Mask", "Encode", "Sink"]
