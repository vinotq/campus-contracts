import re

EMAIL_MAX_LENGTH = 190

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+@[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}$"
)

PHONE_MESSAGE = "Номер телефона должен быть в формате +7XXXXXXXXXX"
EMAIL_MESSAGE = "Почта пишется латиницей, вида ivan@mail.ru"


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits[0] in ("7", "8"):
        digits = "7" + digits[1:]
    if len(digits) != 11 or digits[0] != "7":
        raise ValueError(PHONE_MESSAGE)
    return "+" + digits


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not email or len(email) > EMAIL_MAX_LENGTH or EMAIL_RE.fullmatch(email) is None:
        raise ValueError(EMAIL_MESSAGE)
    return email
