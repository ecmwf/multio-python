import pytest
from pydantic import ValidationError

from multiopython.plans import Config, Plan


def test_sample_config():
    plan = {
        "plans": [
            {
                "actions": [
                    {"type": "print", "stream": "cout", "prefix": " ++ MULTIO-PRINT-ALL-DEBUG :: "},
                    {"type": "encode", "format": "grib", "template": "grib_template.grib", "grid-type": "n320"},
                    {
                        "sinks": [{"append": True, "path": "debug.grib", "per-server": False, "type": "file"}],
                        "type": "sink",
                    },
                ],
                "name": "output-plan",
            }
        ]
    }
    Config(**plan)


def test_add_invalid_action():
    test_plan = Plan(name="testing")
    with pytest.raises(ValidationError):
        test_plan.add_action({"type": "invalid"})


def test_add_valid_action():
    test_plan = Plan(name="testing")
    test_plan.add_action({"type": "print"})
