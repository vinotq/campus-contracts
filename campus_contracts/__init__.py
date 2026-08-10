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

#: Типы, по которым обе стороны приведены к контракту и проверка включена.
#:
#: Список рос по одному типу за раз, вместе с починкой отправителя: включи всё
#: сразу — и проверка на отправке остановила бы обмен целиком вместо того, чтобы
#: чинить его по частям. 10.08.2026 он сравнялся со всеми типами контракта.
#:
#: Новый тип заводится сразу сюда. Тип вне этого списка отправляется без сверки
#: — то есть ровно так, как обмен ломался до всей этой работы.
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
    # Бельё, 10.08.2026. Выдача и долг приведены к ключу кабинета и датам
    # начала периода; состав долга больше не уезжает — кабинет его не хранит.
    "linen.granted",
    "linen.debt_created",
    "linen.debt_acknowledged",
    # Заявки на ремонт, 10.08.2026. У АСПиРС заведены ссылки кабинета и его
    # номер, статус переводится на границе, отзыв наконец применяется.
    "ticket.created",
    "ticket.item_added",
    "ticket.withdrawn",
    "ticket.status_changed",
    # Заявления и пропуска, 10.08.2026. Ссылка кабинета хранится, статусы
    # переводятся на границе, отзыв применяется в обеих очередях.
    "leave.submitted",
    "pass.submitted",
    "application.withdrawn",
    "leave.status_changed",
    "pass.status_changed",
    # Подтверждение приёма, 10.08.2026: единый `message.stored` вместо
    # `<тип>.stored`. Последний непереведённый тип контракта.
    "message.stored",
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
