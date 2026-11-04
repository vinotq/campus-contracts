import pytest
from campus_contracts.downstream import RoundPerson
from pydantic import ValidationError


def test_deadline_is_optional_for_previous_producers():
    row=RoundPerson(aspirs_ref='resident',last_name='Фамилия',first_name='Имя')
    assert row.statement_until is None


def test_deadline_requires_timezone():
    data=dict(aspirs_ref='resident',last_name='Фамилия',first_name='Имя')
    with pytest.raises(ValidationError):
        RoundPerson(**data,statement_until='2026-11-04T22:00:00')
    row=RoundPerson(**data,statement_until='2026-11-04T22:00:00+03:00')
    assert row.statement_until.hour==22
