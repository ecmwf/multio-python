# (C) Copyright 2024 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from typing import Literal, Union

from pydantic import BaseModel, Field


class Sinks(BaseModel):
    """Base Sinks class"""

    type: str


class FDB(Sinks):
    """FDB Sink"""

    type: Literal["fdb"] = "fdb"
    config: str = Field("", title="Config", description="Path to FDB configuration")


class File(Sinks):
    """File Sink"""

    type: Literal["file"] = "file"
    append: bool
    per_server: bool = Field(False, serialization_alias="per-server")
    path: str


class Socket(Sinks):  # TO BE ADDED
    """Socket Sink"""

    type: Literal["socket"] = "socket"


SINKS = Union[FDB, File, Socket]

__all__ = ["Sinks", "FDB", "File", "SINKS"]
