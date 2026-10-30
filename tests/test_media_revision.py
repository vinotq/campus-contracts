import pytest

from campus_contracts import Direction, ValidationError, validate
from campus_contracts.samples import SAMPLES


def test_media_update_carries_complete_snapshot_and_revision():
    sample = SAMPLES[Direction.DOWNSTREAM]["media.request_updated"]
    parsed = validate(Direction.DOWNSTREAM, "media.request_updated", sample)
    assert parsed.revision == 2
    assert parsed.what
    assert parsed.changed_at
    with pytest.raises(ValidationError):
        validate(Direction.DOWNSTREAM, "media.request_updated", dict(sample, revision=1))
    with pytest.raises(ValidationError):
        validate(Direction.DOWNSTREAM, "media.request_updated", {"request_ref": sample["request_ref"]})


def test_old_create_and_feed_messages_keep_legacy_defaults():
    created = validate(
        Direction.DOWNSTREAM, "media.request_created",
        SAMPLES[Direction.DOWNSTREAM]["media.request_created"],
    )
    assert created.revision == 1
    sample = SAMPLES[Direction.UPSTREAM]["media.to_feed"]
    assert validate(Direction.UPSTREAM, "media.to_feed", sample).request_revision is None
    assert validate(
        Direction.UPSTREAM, "media.to_feed", dict(sample, request_revision=2),
    ).request_revision == 2
    with pytest.raises(ValidationError):
        validate(Direction.UPSTREAM, "media.to_feed", dict(sample, request_revision=0))
