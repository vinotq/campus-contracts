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
    schema_for,
    validate,
)
from campus_contracts.envelope import MAX_ROUND_PEOPLE
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


def test_полный_подъезд_влезает_в_сообщение():
    """Единственное место контракта, где размер задаётся произведением.

    У остальных типов длину диктует одно поле, и потолок сообщения им не грозит.
    Здесь список людей умножается на длину каждого, и посчитать это надо здесь:
    иначе первый же большой подъезд с длинными подписями получит 413 на весь
    вечерний обход, и узнаем мы об этом от студента, а не от теста.

    Тела собираются по верхним границам схемы, а не по образцам: образец мал по
    определению, а ломается как раз полный подъезд.
    """
    человек = {
        "aspirs_ref": "Z" * 22,
        "last_name": "Константинопольская-Оглы",
        "first_name": "Александра",
        "middle_name": "Владиславовна",
        "course": 4,
        "floor": 12,
        "room": "1204а",
        "photo_id": "018f2c5e-0000-7000-8000-00000000000c",
        "mark_required": False,
        "note": "З" * 200,
        "temporary_room": "8-1-5333",
    }
    отметка = {
        "aspirs_ref": "Z" * 22,
        "mark": "absent",
        "comment": "К" * 300,
        "marked_by": "Q" * 22,
    }
    тела = {
        (Direction.DOWNSTREAM, "round.roster"): {
            "round_date": "2026-08-12",
            "building": "8",
            "entrance": "2",
            "people": [человек] * MAX_ROUND_PEOPLE,
        },
        (Direction.UPSTREAM, "round.submitted"): {
            "round_date": "2026-08-12",
            "building": "8",
            "entrance": "2",
            "submitted_by": "Z" * 22,
            "submitted_at": "2026-08-12T22:40:00+03:00",
            "auto_closed": False,
            "marks": [отметка] * MAX_ROUND_PEOPLE,
        },
    }
    for (direction, message_type), body in тела.items():
        validate(direction, message_type, body)
        размер = len(json.dumps(body, ensure_ascii=False).encode())
        assert размер <= MAX_MESSAGE_BYTES, (message_type, размер)


def test_образцов_не_больше_чем_типов():
    for direction, samples in SAMPLES.items():
        assert set(samples) <= set(SCHEMAS[direction]), "образец на тип вне контракта"


def test_включённая_проверка_ссылается_на_существующие_типы():
    known = set(SCHEMAS[Direction.DOWNSTREAM]) | set(SCHEMAS[Direction.UPSTREAM])
    assert ENFORCED <= known


def test_переведены_все_типы():
    """Список рос по одному типу за раз, вместе с починкой отправителя.

    10.08.2026 он сравнялся со всеми типами контракта: обе стороны приведены
    целиком. Проверка нужна и дальше — новый тип, заведённый без включения в
    `ENFORCED`, отправлялся бы без сверки, то есть ровно так, как ломался обмен
    до всей этой работы.
    """
    known = set(SCHEMAS[Direction.DOWNSTREAM]) | set(SCHEMAS[Direction.UPSTREAM])
    assert ENFORCED == known


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


#: Сообщения, адресованные не человеку. У них ключа человека нет на верхнем
#: уровне, и это не упущение: раскладка главной принадлежит кабинету целиком, а
#: три типа обхода — подъезду и дате. Люди внутри них лежат списком, и там ключ
#: тот же самый, `aspirs_ref`.
БЕЗ_ЧЕЛОВЕКА = frozenset({
    "message.stored",
    "home.layout",
    "round.roster",
    "round.extended",
    "round.submitted",
})


def test_человек_везде_один_и_тот_же_ключ():
    """`resident_ref` и `employee_id` из контракта убраны намеренно."""
    for direction, schemas in SCHEMAS.items():
        for message_type, schema in schemas.items():
            fields = set(schema.model_fields)
            assert "resident_ref" not in fields, message_type
            assert "employee_id" not in fields, message_type
            if any(f.endswith("_ref") for f in fields) or "aspirs_ref" in fields:
                continue
            assert message_type in БЕЗ_ЧЕЛОВЕКА, (direction, message_type)


def test_человек_внутри_списков_тоже_aspirs_ref():
    """Список людей внутри сообщения — то же место, где ключи расходились.

    Проверка верхнего уровня его не ловит: `round.roster` и `round.submitted`
    адресованы подъезду, а люди у них вложены. Ровно так и разъезжаются схемы —
    снаружи всё сходится, внутри у каждого своё имя поля.
    """
    вложенные = [
        SCHEMAS[Direction.DOWNSTREAM]["round.roster"].model_fields["people"],
        SCHEMAS[Direction.UPSTREAM]["round.submitted"].model_fields["marks"],
    ]
    for field in вложенные:
        item = field.annotation.__args__[0]
        assert "aspirs_ref" in item.model_fields, item.__name__
