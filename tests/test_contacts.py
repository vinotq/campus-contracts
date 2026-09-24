import pytest

from campus_contracts.contacts import normalize_email, normalize_phone


@pytest.mark.parametrize("raw", ["8 (900) 555-44-33", "+7 900 555 44 33", "79005554433"])
def test_a_russian_mobile_is_brought_to_one_form(raw):
    assert normalize_phone(raw) == "+79005554433"


@pytest.mark.parametrize("raw", ["9005554433", "12345", "+1 900 555 44 33"])
def test_anything_else_is_not_a_phone(raw):
    with pytest.raises(ValueError):
        normalize_phone(raw)


def test_an_email_is_lowercased():
    assert normalize_email(" Ivan@Mail.RU ") == "ivan@mail.ru"


@pytest.mark.parametrize("raw", ["", "ivan", "иван@почта.рф", "ivan@mail"])
def test_a_bad_email_is_refused(raw):
    with pytest.raises(ValueError):
        normalize_email(raw)
