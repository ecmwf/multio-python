import pytest

from multiopython.plans.actions import Aggregation, Encode, Mask, Print, Select, Sink, Transport


@pytest.mark.parametrize(
    ("action", "type", "kwargs"),
    (
        (Select, "select", {"match": [{"category": "custom"}]}),
        (Print, "print", {"stream": "cout", "prefix": " ++ MULTIO-PRINT-ALL-DEBUG :: "}),
        (Mask, "mask", {}),
        (Encode, "encode", {"format": "grib", "template": "template", "grid_type": "grid_type"}),
        (Transport, "transport", {"target": "target"}),
        (Aggregation, "aggregation", {}),
        (Sink, "sink", {"sinks": [{"append": True, "path": "debug.grib", "per-server": False, "type": "file"}]}),
    ),
)
def test_action_default_values(action, type, kwargs):
    action_cls = action(**kwargs)
    assert action_cls.type == type
