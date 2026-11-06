import pytest
from pydantic import ValidationError
from campus_contracts import Direction, validate
from campus_contracts.samples import SAMPLES


def check(body):
    return validate(Direction.UPSTREAM, "post.read_stats", body)


def test_aggregate_and_real_zero_have_no_personal_identifiers():
    body = SAMPLES[Direction.UPSTREAM]["post.read_stats"]
    parsed = check(body)
    assert parsed.items[0].reads == 29
    assert set(parsed.items[0].model_dump()) == {"post_ref", "reads", "audience_total"}
    check({**body, "items": [{"post_ref": "7", "reads": 0, "audience_total": 0}]})


@pytest.mark.parametrize(
    "item",
    [
        {"post_ref": "7", "reads": -1, "audience_total": 2},
        {"post_ref": "7", "reads": 3, "audience_total": 2},
        {"post_ref": "7", "reads": True, "audience_total": 2},
        {"post_ref": "7", "reads": 1, "audience_total": -1},
        {"post_ref": "7", "reads": 1, "audience_total": 2, "resident_ref": "private"},
    ],
)
def test_invalid_counts_or_personal_data_rejected(item):
    with pytest.raises(ValidationError):
        check({"observed_at": "2026-11-06T10:00:00Z", "items": [item]})


@pytest.mark.parametrize("count", [0, 51])
def test_bounded_batch(count):
    with pytest.raises(ValidationError):
        check(
            {
                "observed_at": "2026-11-06T10:00:00Z",
                "items": [
                    {"post_ref": str(i), "reads": 0, "audience_total": 1} for i in range(count)
                ],
            }
        )


def test_repeated_post_and_missing_timezone_rejected():
    body = SAMPLES[Direction.UPSTREAM]["post.read_stats"]
    with pytest.raises(ValidationError):
        check({**body, "items": body["items"] * 2})
    with pytest.raises(ValidationError):
        check({**body, "observed_at": "2026-11-06T10:00:00"})
