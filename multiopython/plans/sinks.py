from typing import Literal

from pydantic import BaseModel, Field


class Sinks(BaseModel):
    """Base Sinks class"""

    type: str


class FDB(Sinks):
    """FDB Sink"""

    type: Literal["fdb"] = "fdb"
    config: dict = Field({}, title="Config", description="FDB configuration")


class File(Sinks):
    """File Sink"""

    type: Literal["file"] = "file"
    append: bool
    per_server: bool = Field(False, serialization_alias="per-server")
    path: str


class Socket(Sinks):  # TO BE ADDED
    """Socket Sink"""

    type: Literal["socket"] = "socket"


SINKS = {"fdb": FDB, "file": File}

__all__ = ["Sinks", "FDB", "File", "SINKS"]
