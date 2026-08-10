"""Контракт обмена АСПиРС ↔ Шлюз ↔ ЛКП.

Единственное описание того, что внутри сообщений. До него стороны знали список
типов и придумывали поля каждая себе, отчего в кабинет не применялось почти
ничего, а узнать об этом было неоткуда: у принимающей стороны `extra="forbid"`,
и отказ тихо ложился строкой в чужой журнал.

Пользоваться так::

    from campus_contracts import Direction, validate, is_enforced

    if is_enforced(message_type):
        validate(Direction.DOWNSTREAM, message_type, payload)

Разбор человеческой части — в `CONTRACT.md` этого же репозитория.
"""

from enum import StrEnum

from pydantic import ValidationError

from campus_contracts import downstream, upstream, values
from campus_contracts.envelope import (
    MAX_BATCH,
    MAX_MESSAGE_BYTES,
    SCHEMA_VERSION,
    Audience,
    Batch,
    Envelope,
    Strict,
)


class Direction(StrEnum):
    #: Из АСПиРС в кабинет.
    DOWNSTREAM = "downstream"
    #: Из кабинета в АСПиРС.
    UPSTREAM = "upstream"


SCHEMAS = {
    Direction.DOWNSTREAM: downstream.SCHEMAS,
    Direction.UPSTREAM: upstream.SCHEMAS,
}

#: Типы, по которым обе стороны уже приведены к контракту и проверка включена.
#:
#: Список растёт по мере очередей 3 и 4 плана, по одному типу за раз. Включать
#: всё сразу нельзя: пока отправитель шлёт старые поля, проверка на отправке
#: остановила бы обмен целиком вместо того, чтобы починить его по частям.
ENFORCED = frozenset({
    "profile.updated",
    "account.invited",
    "account.blocked",
    "account.unblocked",
    "device.registered",
    # Публикации, 10.08.2026. У АСПиРС заведены рубрика, адрес раздела и
    # подпись — до этого им негде было взяться, а кабинет их ждал.
    "news.published",
    "news.updated",
    "news.deleted",
    "event.published",
    "event.updated",
    "notice.urgent",
})


class UnknownMessageType(ValueError):
    """Тип отсутствует в контракте. Опечатка либо самодеятельность."""


def is_enforced(message_type: str) -> bool:
    return message_type in ENFORCED


def schema_for(direction: Direction, message_type: str) -> type[Strict]:
    try:
        return SCHEMAS[direction][message_type]
    except KeyError:
        raise UnknownMessageType(
            f"типа {message_type} нет в контракте направления {direction}"
        ) from None


def validate(direction: Direction, message_type: str, payload: dict) -> Strict:
    """Разобрать тело схемой контракта. Бросает `ValidationError`.

    Вызывается **на отправке тоже**, а не только на приёме: отправитель — та
    сторона, которая может исправить ошибку, и узнавать о ней из чужого журнала
    через неделю по жалобе коменданта не годится.
    """
    return schema_for(direction, message_type).model_validate(payload)


__all__ = [
    "MAX_BATCH",
    "MAX_MESSAGE_BYTES",
    "SCHEMA_VERSION",
    "SCHEMAS",
    "ENFORCED",
    "Audience",
    "Batch",
    "Direction",
    "Envelope",
    "Strict",
    "UnknownMessageType",
    "ValidationError",
    "downstream",
    "upstream",
    "values",
    "is_enforced",
    "schema_for",
    "validate",
]
