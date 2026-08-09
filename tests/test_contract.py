"""Проверки самого контракта.

Не «работает ли pydantic», а то, что легко разъехалось бы незаметно: у каждого
типа есть схема и годный образец, лишнее поле отвергается, а включённая
проверка не ссылается на тип, которого нет.
"""

import json

import pytest
from pydantic import ValidationError

from campus_contracts import (
    ENFORCED,
    MAX_MESSAGE_BYTES,
    SCHEMA_VERSION,
    SCHEMAS,
    Direction,
    Envelope,
    UnknownMessageType,
    is_enforced,
    schema_for,
    validate,
)
from campus_contracts.samples import SAMPLES

ALL_TYPES = [
    (direction, message_type)
    for direction, schemas in SCHEMAS.items()
    for message_type in schemas
]


@pytest.mark.parametrize(("direction", "message_type"), ALL_TYPES)
def test_у_каждого_типа_есть_годный_образец(direction, message_type):
    assert message_type in SAMPLES[direction], "образец нужен всем: им проверяются отправители"
    validate(direction, message_type, SAMPLES[direction][message_type])


@pytest.mark.parametrize(("direction", "message_type"), ALL_TYPES)
def test_лишнее_поле_отвергается(direction, message_type):
    """Ровно так ломался обмен: поле переименовали, сообщение отбросили молча."""
    body = dict(SAMPLES[direction][message_type], лишнее="поле")
    with pytest.raises(ValidationError):
        validate(direction, message_type, body)


@pytest.mark.parametrize(("direction", "message_type"), ALL_TYPES)
def test_образец_переживает_дорогу(direction, message_type):
    """По каналу тело едет строкой, а не объектом Python."""
    body = json.loads(json.dumps(SAMPLES[direction][message_type], ensure_ascii=False))
    validate(direction, message_type, body)
    assert len(json.dumps(body).encode()) <= MAX_MESSAGE_BYTES


def test_образцов_не_больше_чем_типов():
    for direction, samples in SAMPLES.items():
        assert set(samples) <= set(SCHEMAS[direction]), "образец на тип вне контракта"


def test_включённая_проверка_ссылается_на_существующие_типы():
    known = set(SCHEMAS[Direction.DOWNSTREAM]) | set(SCHEMAS[Direction.UPSTREAM])
    assert ENFORCED <= known


def test_включено_только_то_что_уже_переведено():
    """Список растёт по одному типу за раз, вместе с починкой отправителя.

    Если он вдруг сравнялся со всеми типами — значит кто-то включил проверку
    оптом, и первый же старый отправитель встанет.
    """
    known = set(SCHEMAS[Direction.DOWNSTREAM]) | set(SCHEMAS[Direction.UPSTREAM])
    assert ENFORCED != known or not known
    assert is_enforced("profile.updated")
    assert not is_enforced("linen.granted")


def test_неизвестный_тип_называет_себя():
    with pytest.raises(UnknownMessageType) as exc:
        schema_for(Direction.DOWNSTREAM, "news.почти_published")
    assert "news.почти_published" in str(exc.value)


def test_конверт_принимает_адресацию_и_отвергает_прочее():
    envelope = {
        "id": "018f2c5e-0000-7000-8000-000000000001",
        "type": "news.published",
        "version": SCHEMA_VERSION,
        "occurred_at": "2026-08-04T12:00:00+03:00",
        "audience": {"buildings": ["8"], "courses": [1], "groups": []},
        "payload": SAMPLES[Direction.DOWNSTREAM]["news.published"],
    }
    assert Envelope.model_validate(envelope).type == "news.published"

    with pytest.raises(ValidationError):
        Envelope.model_validate(dict(envelope, отправитель="аспирс"))


def test_статусы_не_принимают_чужих_значений():
    """`in_work` — внутреннее слово АСПиРС, переводится на границе."""
    body = dict(SAMPLES[Direction.DOWNSTREAM]["ticket.status_changed"], status="in_work")
    with pytest.raises(ValidationError):
        validate(Direction.DOWNSTREAM, "ticket.status_changed", body)


def test_человек_везде_один_и_тот_же_ключ():
    """`resident_ref` и `employee_id` из контракта убраны намеренно."""
    for direction, schemas in SCHEMAS.items():
        for message_type, schema in schemas.items():
            fields = set(schema.model_fields)
            assert "resident_ref" not in fields, message_type
            assert "employee_id" not in fields, message_type
            if any(f.endswith("_ref") for f in fields) or "aspirs_ref" in fields:
                continue
            assert message_type in ("message.stored",), (direction, message_type)
