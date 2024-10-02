import pytest
from pydantic import ValidationError

import multiopython
from multiopython.plans import Config, Plan

sample_plan = {
    "plans": [
        {
            "actions": [
                {"type": "print", "stream": "cout", "prefix": " ++ MULTIO-PRINT-ALL-DEBUG :: "},
                {
                    "sinks": [{"append": True, "path": "debug.grib", "per-server": False, "type": "file"}],
                    "type": "sink",
                },
            ],
            "name": "output-plan",
        }
    ]
}


def test_sample_config():
    Config(**sample_plan)


def test_with_multio_server_sample():
    config = Config(**sample_plan)
    with multiopython.MultioPlan(config):
        with multiopython.Multio() as multio_object:
            pass


def test_with_multio_server_empty():
    config = Config(name="empty")
    with multiopython.MultioPlan(config):
        with multiopython.Multio() as multio_object:
            pass


def test_with_multio_server_add():
    config = Config(name="empty")
    config.add_plan(Plan(name="print", actions=[{"type": "print"}]))
    with multiopython.MultioPlan(config):
        with multiopython.Multio() as multio_object:
            pass


def test_add_invalid_action():
    test_plan = Plan(name="testing")
    with pytest.raises(ValidationError):
        test_plan.add_action({"type": "invalid"})


def test_missing_key_action():
    test_plan = Plan(name="testing")
    with pytest.raises(ValidationError):
        test_plan.add_action({"type": "encode"})


def test_add_valid_action():
    test_plan = Plan(name="testing")
    test_plan.add_action({"type": "print"})


def test_conversion_to_config():
    test_plan = Plan(name="testing", actions=[{"type": "print"}])
    test_config = test_plan.to_config()
    assert isinstance(test_config, Config)
    assert test_plan == test_config.plans[0]


def test_auto_add_sink():
    test_plan = Plan(name="testing", actions=[{"type": "print"}])
    assert len(test_plan.actions) == 2
    assert test_plan.actions[-1].type == "sink"
