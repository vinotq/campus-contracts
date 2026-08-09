"""Из кабинета в АСПиРС.

До этого пакета описания у направления не было вовсе: приёмники читали
`payload["employee_id"]` руками, а отправитель клал `resident_ref`, и не
совпадало ничего.
"""

from datetime import date, datetime

from pydantic import Field

from campus_contracts.envelope import Strict

#: Больше гостей за раз в пропуск не пускают.
MAX_VISITORS = 10


class TicketItem(Strict):
    """Проблема внутри заявки на ремонт."""

    ref: str = Field(max_length=64)
    position: int = Field(ge=1)
    text: str = Field(min_length=1, max_length=2000)
    is_urgent: bool = False
    #: Идентификаторы снимков. Файлы идут отдельным потоком по одноразовой
    #: ссылке: вложений в сообщении контракт не допускает.
    photos: list[str] = Field(default_factory=list, max_length=16)


class TicketCreated(Strict):
    """Заявка на ремонт, поданная студентом.

    `place_note` — уточнение места одной строкой: кабинет собирает его из своих
    «места» и «комнаты», заводить под них две колонки в АСПиРС ради одной
    строки на экране незачем.
    """

    ticket_ref: str = Field(max_length=64)
    number: str = Field(max_length=32)
    aspirs_ref: str = Field(max_length=64)
    place: str = Field(max_length=32)
    place_note: str | None = Field(default=None, max_length=255)
    items: list[TicketItem] = Field(min_length=1, max_length=20)


class TicketItemAdded(Strict):
    ticket_ref: str = Field(max_length=64)
    item: TicketItem


class TicketWithdrawn(Strict):
    """Студент закрыл заявку сам. Дописывать её после этого нельзя."""

    ticket_ref: str = Field(max_length=64)


class LeaveSubmitted(Strict):
    """Заявление на выход.

    `scan` — обычный скан, а не особый вид документа: несовершеннолетний
    прикладывает согласие родителя, совершеннолетний — что понадобилось, и
    хранятся они одинаково.
    """

    application_ref: str = Field(max_length=64)
    number: str = Field(max_length=32)
    aspirs_ref: str = Field(max_length=64)
    from_at: datetime
    #: Пусто — до возвращения, без заранее известного срока.
    to_at: datetime | None = None
    reason: str | None = Field(default=None, max_length=2000)
    scan: str | None = Field(default=None, max_length=64)
    #: Согласие родителя голосом в чате вместо бумаги.
    voice_in_chat: bool = False


class Visitor(Strict):
    """Гость в пропуске.

    `document` — единственные ПДн, которые кабинет хранить не должен: он стирает
    их, получив `message.stored`.
    """

    position: int = Field(ge=1)
    fio: str = Field(min_length=1, max_length=200)
    relation: str | None = Field(default=None, max_length=100)
    document: str | None = Field(default=None, max_length=64)


class Car(Strict):
    make: str = Field(max_length=100)
    plate: str = Field(min_length=1, max_length=32)


class PassSubmitted(Strict):
    """Пропуск для родных. Машин список, а не одна: приезжают и на двух."""

    application_ref: str = Field(max_length=64)
    number: str = Field(max_length=32)
    aspirs_ref: str = Field(max_length=64)
    from_date: date
    to_date: date
    visitors: list[Visitor] = Field(min_length=1, max_length=MAX_VISITORS)
    cars: list[Car] = Field(default_factory=list, max_length=4)


class ApplicationWithdrawn(Strict):
    application_ref: str = Field(max_length=64)


class LinenDebtAcknowledged(Strict):
    """АСПиРС ищет долг по человеку и периоду: своего номера у кабинета нет."""

    aspirs_ref: str = Field(max_length=64)
    period_start: date


class DeviceRegistered(Strict):
    """Кабинет заработал: студент вошёл с устройства.

    Отдельного «активирован» в контракте нет — вход с устройства и означает,
    что код сгорел и в кабинет вошли.
    """

    aspirs_ref: str = Field(max_length=64)


#: Тип сообщения → схема тела.
SCHEMAS = {
    "ticket.created": TicketCreated,
    "ticket.item_added": TicketItemAdded,
    "ticket.withdrawn": TicketWithdrawn,
    "leave.submitted": LeaveSubmitted,
    "pass.submitted": PassSubmitted,
    "application.withdrawn": ApplicationWithdrawn,
    "linen.debt_acknowledged": LinenDebtAcknowledged,
    "device.registered": DeviceRegistered,
}
