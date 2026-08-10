"""Из АСПиРС в кабинет.

Человек всюду `aspirs_ref` — непрозрачный идентификатор кабинета студента. Не
внутренний номер и не uuid проживающего в ЛКП: по одному ключу не должны
открываться две системы сразу, а второй стороне он всё равно неизвестен.
"""

from datetime import date, datetime

from pydantic import Field

from campus_contracts.envelope import Audience, Strict
from campus_contracts.values import (
    ApplicationStatus,
    CodePurpose,
    ItemStatus,
    LinenMethod,
    PostKind,
    ResidencyStatus,
)

# ── Публикации ───────────────────────────────────────────────────────────────


class PostPublished(Strict):
    """Новость, событие или страница справочной.

    Аудитория дублируется в конверте и здесь намеренно: конверт читает Шлюз,
    тело — кабинет, и разбирать чужое ради маршрутизации никто не должен.
    """

    aspirs_ref: str = Field(max_length=64)
    kind: PostKind
    title: str = Field(min_length=1, max_length=300)
    #: Markdown, не HTML. Принимать HTML из внешней системы значит открыть XSS
    #: через чужой модуль публикаций.
    body_md: str = Field(max_length=100_000)
    rubric: str | None = Field(default=None, max_length=48)
    author_label: str | None = Field(default=None, max_length=160)
    is_urgent: bool = False
    #: Только справочная: адрес раздела и порядок в списке.
    slug: str | None = Field(default=None, max_length=64)
    sort_order: int = 0
    published_at: datetime
    audience: Audience = Field(default_factory=Audience)
    #: Галерея по порядку. Здесь только идентификаторы: файлы идут отдельным
    #: потоком по одноразовой ссылке, вкладывать их в сообщение нельзя.
    image_ids: list[str] = Field(default_factory=list, max_length=32)


class PostDeleted(Strict):
    aspirs_ref: str = Field(max_length=64)


class NoticeUrgent(Strict):
    """Срочное объявление — пинок, а не публикация.

    Тело кабинет уже получил основным потоком. Здесь только то, ради чего
    студента будят пушем, и никаких ПДн.
    """

    aspirs_ref: str = Field(max_length=64)
    title: str = Field(min_length=1, max_length=300)


# ── Карточка ─────────────────────────────────────────────────────────────────


class ProfileUpdated(Strict):
    """Витрина карточки студента.

    Минимум, достаточный для экрана, а не копия карточки из АСПиРС. Паспорта,
    СНИЛС, диагнозов, взысканий и законных представителей здесь нет и не должно
    появиться.
    """

    aspirs_ref: str = Field(max_length=64)
    #: Однословное ФИО из выгрузки Opera даёт имя «—»: кривая строка импорта не
    #: должна отменять всю карточку.
    last_name: str = Field(min_length=1, max_length=120)
    first_name: str = Field(min_length=1, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    #: Курса в АСПиРС нет вовсе, поэтому сейчас всегда пусто.
    course: int | None = Field(default=None, ge=1, le=9)
    study_group: str | None = Field(default=None, max_length=64)
    building: str | None = Field(default=None, max_length=16)
    entrance: str | None = Field(default=None, max_length=16)
    room: str | None = Field(default=None, max_length=32)
    #: Второй фактор при активации. Пустая — код не подойдёт никогда.
    birth_date: date | None = None
    is_adult: bool = True
    residency_status: ResidencyStatus = ResidencyStatus.LIVING
    #: Только цифры: кабинет ищет по ним учётную запись при входе.
    phone: str | None = Field(default=None, max_length=32)
    #: Нижним регистром, по той же причине.
    email: str | None = Field(default=None, max_length=190)
    telegram: str | None = Field(default=None, max_length=64)
    vk: str | None = Field(default=None, max_length=190)


# ── Заявки и заявления ───────────────────────────────────────────────────────


class TicketStatusChanged(Strict):
    """Одно сообщение на позицию, а не пачка.

    Кабинет обновляет позицию и пишет событие в ленту заявки. Из пачки ему
    пришлось бы вычислять, что изменилось, — отправитель это знает и так.
    """

    ticket_ref: str = Field(max_length=64)
    item_ref: str = Field(max_length=64)
    status: ItemStatus
    note: str | None = Field(default=None, max_length=2000)
    reject_reason: str | None = Field(default=None, max_length=2000)


class ApplicationStatusChanged(Strict):
    """Статус заявления на выход или пропуска.

    `decided_at` не передаётся: кабинет ставит собственное время события в
    ленте, и второе время рядом с ним только путало бы.
    """

    application_ref: str = Field(max_length=64)
    status: ApplicationStatus
    note: str | None = Field(default=None, max_length=2000)
    decline_reason: str | None = Field(default=None, max_length=2000)


# ── Бельё ────────────────────────────────────────────────────────────────────


class LinenGranted(Strict):
    aspirs_ref: str = Field(max_length=64)
    period_start: date
    granted_at: datetime
    method: LinenMethod = LinenMethod.QR
    #: Подпись для экрана, а не логин сотрудника.
    granted_by: str | None = Field(default=None, max_length=120)


class LinenDebtCreated(Strict):
    """Состав долга не передаётся: кабинет его не хранит и не показывает."""

    aspirs_ref: str = Field(max_length=64)
    period_start: date


# ── Кабинеты ─────────────────────────────────────────────────────────────────


class AccountInvited(Strict):
    """Код активации, выданный комендантом.

    Приезжает хешем, а не открытым текстом: код диктуют студенту голосом, и по
    каналу ему ходить незачем.
    """

    aspirs_ref: str = Field(max_length=64)
    #: sha256 от кода в верхнем регистре, шестнадцатеричной строкой.
    code_hash: str = Field(min_length=64, max_length=64)
    expires_at: datetime
    purpose: CodePurpose = CodePurpose.ACTIVATION


class AccountBlocked(Strict):
    aspirs_ref: str = Field(max_length=64)
    #: Показывается студенту при попытке входа.
    reason: str | None = Field(default=None, max_length=500)


class MessageStored(Strict):
    """«Записал у себя, можно стирать».

    Один тип на все подтверждения, а не `<тип>.stored` на каждое. Пока оно не
    придёт, кабинет держит у себя цифры паспортов гостей.
    """

    message_id: str = Field(max_length=64)


#: Тип сообщения → схема тела.
SCHEMAS = {
    "news.published": PostPublished,
    "news.updated": PostPublished,
    "news.deleted": PostDeleted,
    "event.published": PostPublished,
    "event.updated": PostPublished,
    "notice.urgent": NoticeUrgent,
    "profile.updated": ProfileUpdated,
    "ticket.status_changed": TicketStatusChanged,
    "leave.status_changed": ApplicationStatusChanged,
    "pass.status_changed": ApplicationStatusChanged,
    "linen.granted": LinenGranted,
    "linen.debt_created": LinenDebtCreated,
    "account.invited": AccountInvited,
    "account.blocked": AccountBlocked,
    "account.unblocked": AccountBlocked,
    "message.stored": MessageStored,
}
