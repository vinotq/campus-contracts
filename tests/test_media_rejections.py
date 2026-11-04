import pytest

from campus_contracts import Direction, ValidationError, validate
from campus_contracts.samples import SAMPLES


@pytest.mark.parametrize(
    ("message", "field"),
    [("media.request_status_changed", "reject_reason"), ("post.reviewed", "comment")],
)
def test_final_rejection_requires_a_reason(message, field):
    data = {**SAMPLES[Direction.UPSTREAM][message]}
    data["status" if message.startswith("media.") else "verdict"] = "rejected"
    for reason in (None, "", "   "):
        with pytest.raises(ValidationError):
            validate(Direction.UPSTREAM, message, {**data, field: reason})
    result = validate(Direction.UPSTREAM, message, {**data, field: "Не соответствует требованиям"})
    assert getattr(result, field) == "Не соответствует требованиям"
