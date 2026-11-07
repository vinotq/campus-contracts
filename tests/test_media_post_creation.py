from copy import deepcopy

import pytest
from pydantic import ValidationError

from campus_contracts import Direction, validate
from campus_contracts.samples import UPSTREAM


def test_standalone_media_post_has_distinct_schema():
    result = validate(Direction.UPSTREAM, "post.created", deepcopy(UPSTREAM["post.created"]))
    assert str(result.local_ref) == UPSTREAM["post.created"]["local_ref"]


@pytest.mark.parametrize("field,value", [
    ("local_ref", "not-a-uuid"), ("author_ref", ""), ("reviewer_ref", ""),
    ("title", "x" * 256), ("body_md", "x" * 20001),
    ("decided_at", "2026-11-07T12:00:00"),
])
def test_media_creation_rejects_invalid_identity_limits_and_naive_time(field, value):
    data = deepcopy(UPSTREAM["post.created"])
    data[field] = value
    with pytest.raises(ValidationError):
        validate(Direction.UPSTREAM, "post.created", data)
