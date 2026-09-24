"""Из кабинета в АСПиРС.

До этого пакета описания у направления не было вовсе: приёмники читали
`payload["employee_id"]` руками, а отправитель клал `resident_ref`, и не
совпадало ничего.
"""

from datetime import date, datetime, time

from pydantic import Field

from campus_contracts.envelope import MAX_ROUND_PEOPLE, Strict
from campus_contracts.values import RoundMark

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
    #: Час приезда и отъезда. Без него охрана читает пропуск как «весь день»,
    #: а кабинет спрашивает время с прототипа 52V и хранит его у себя.
    #: Необязательные: у пропусков, поданных до этой правки, времени нет.
    from_time: time | None = None
    to_time: time | None = None
    visitors: list[Visitor] = Field(min_length=1, max_length=MAX_VISITORS)
    cars: list[Car] = Field(default_factory=list, max_length=4)


class ApplicationWithdrawn(Strict):
    application_ref: str = Field(max_length=64)


class LinenDebtAcknowledged(Strict):
    """АСПиРС ищет долг по человеку и периоду: своего номера у кабинета нет."""

    aspirs_ref: str = Field(max_length=64)
    period_start: date


class LinenCollected(Strict):
    """Бельё выдано по коду на станции прачечной.

    Выдачу отмечает кабинет: у станции нет ни учётки, ни маршрута в АСПиРС.
    `by_proxy` — код был пересланный, бельё забрал не сам студент.
    """

    aspirs_ref: str = Field(max_length=64)
    period_start: date
    collected_at: datetime
    by_proxy: bool = False
    #: Подпись станции для журнала, а не её идентификатор.
    station: str = Field(min_length=1, max_length=64)


class DeviceRegistered(Strict):
    """Кабинет заработал: студент вошёл с устройства.

    Отдельного «активирован» в контракте нет — вход с устройства и означает,
    что код сгорел и в кабинет вошли.
    """

    aspirs_ref: str = Field(max_length=64)


class RoundReadiness(Strict):
    """«Иду сегодня».

    Единственное, что кабинет отправляет наверх до обхода, и единственное, что
    работает в закрытом кабинете: принимается весь день до часа раздачи. В
    раздачу попадают только отметившиеся, поэтому без этого сообщения ротация
    получает пустой список.

    `ready` булево, а не «отметился»: передумать до раздачи можно.
    """

    aspirs_ref: str = Field(max_length=64)
    round_date: date
    ready: bool


class RoundMarkItem(Strict):
    """Отметка по одному человеку."""

    aspirs_ref: str = Field(max_length=64)
    mark: RoundMark
    #: Свободный текст про местонахождение: у принимающей стороны он попадает
    #: под шифрование, как и всякие сведения о человеке.
    #:
    #: Короче прочих свободных полей контракта намеренно. Это подпись «сказали,
    #: уехал к родителям», а не объяснительная, и умножается она на весь
    #: подъезд: при потолке в две тысячи знаков полный подъезд не влезал в
    #: сообщение впятеро.
    comment: str | None = Field(default=None, max_length=300)
    #: Кто отметил. Отметки принадлежат подъезду и дате, а не тому, кто их
    #: ставил, поэтому при переназначении посреди обхода в одном подъезде их
    #: бывает двое. Пусто у тех, кого никто не отметил.
    marked_by: str | None = Field(default=None, max_length=64)


class RoundSubmitted(Strict):
    """Обход по подъезду закрыт.

    По одному подъезду приходит несколько раз: сначала автозакрытие в конце
    вечера, потом продление ночного, потом закрытие продления. Верным считается
    последнее пришедшее — второй обход на ту же дату и подъезд заводить нельзя.

    Приходит целиком, включая неотмеченных: иначе принимающая сторона не
    отличит «до человека не дошли» от «человека не было в списке».
    """

    round_date: date
    building: str = Field(min_length=1, max_length=16)
    entrance: str = Field(min_length=1, max_length=16)
    #: Пусто при автозакрытии: кнопку никто не нажимал.
    submitted_by: str | None = Field(default=None, max_length=64)
    submitted_at: datetime
    auto_closed: bool = False
    marks: list[RoundMarkItem] = Field(default_factory=list, max_length=MAX_ROUND_PEOPLE)


#: Тип сообщения → схема тела.
SCHEMAS = {
    "ticket.created": TicketCreated,
    "ticket.item_added": TicketItemAdded,
    "ticket.withdrawn": TicketWithdrawn,
    "leave.submitted": LeaveSubmitted,
    "pass.submitted": PassSubmitted,
    "application.withdrawn": ApplicationWithdrawn,
    "linen.debt_acknowledged": LinenDebtAcknowledged,
    "linen.collected": LinenCollected,
    "device.registered": DeviceRegistered,
    "round.readiness": RoundReadiness,
    "round.submitted": RoundSubmitted,
}
