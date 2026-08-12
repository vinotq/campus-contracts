"""Из АСПиРС в кабинет.

Человек всюду `aspirs_ref` — непрозрачный идентификатор кабинета студента. Не
внутренний номер и не uuid проживающего в ЛКП: по одному ключу не должны
открываться две системы сразу, а второй стороне он всё равно неизвестен.
"""

from datetime import date, datetime, time

from pydantic import Field

from campus_contracts.envelope import MAX_ROUND_PEOPLE, Audience, Strict
from campus_contracts.values import (
    ApplicationStatus,
    CodePurpose,
    HomeBlockKind,
    ItemStatus,
    LinenMethod,
    PostKind,
    ResidencyStatus,
    ResidentRole,
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
    #: Одна рубрика строкой – прежняя форма. Оставлена, чтобы выкладка сторон
    #: в разные дни не роняла приём: отправитель шлёт либо её, либо список.
    rubric: str | None = Field(default=None, max_length=48)
    #: Рубрик у публикации бывает несколько: «Двор» и «Важно» одновременно.
    #: Значения из справочника АСПиРС, свободного ввода нет.
    rubrics: list[str] = Field(default_factory=list, max_length=8)
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


class HomeBlock(Strict):
    """Один блок главной кабинета.

    `key` — стабильная ссылка на блок: по нему кабинет узнаёт свой блок в новой
    раскладке и не пересобирает экран заново на каждое сообщение. У штатных это
    имя вида, у своих — идентификатор из АСПиРС строкой.

    Текст и ссылка есть только у `custom`: остальные блоки кабинет собирает из
    своих данных, и присланный туда текст было бы некуда деть.
    """

    key: str = Field(min_length=1, max_length=64)
    kind: HomeBlockKind
    title: str | None = Field(default=None, max_length=120)
    body_md: str | None = Field(default=None, max_length=4_000)
    link_url: str | None = Field(default=None, max_length=500)
    link_label: str | None = Field(default=None, max_length=60)
    sort_order: int = 0


class HomeLayout(Strict):
    """Главная целиком, снимком.

    Не «переставили блок» и не «добавили блок», а весь список сразу: раскладка
    маленькая, а порядок применения отдельных правок пришлось бы гарантировать,
    чего очередь не умеет. Пришедший снимок заменяет прежний.
    """

    blocks: list[HomeBlock] = Field(default_factory=list, max_length=32)


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

    Тем же сообщением едет и комментарий сотрудника: «в работе, но раньше
    двадцать первого не сделаем». Статус при этом не меняется, поэтому
    принимающая сторона обязана смотреть не только на него — иначе «ничего не
    изменилось» отбрасывает единственное, ради чего сообщение и послали.
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


class AccountRolesUpdated(Strict):
    """Теги студента: полный текущий набор, а не «выдали» и «отобрали».

    Приращения потребовали бы, чтобы обе стороны одинаково считали порядок
    сообщений, а очередь его не гарантирует: потерянное «отобрали» оставило бы
    человеку доступ навсегда. Полный набор самоисправляется — следующее же
    сообщение приводит теги в порядок.

    Пустой список означает, что тегов не осталось, и в этом году это и есть
    закрытие кабинета: учётная запись без единого тега в него не входит.
    Поэтому снятие обязано доехать — по нему кабинет гасит сессии, иначе снятый
    с обходов студент доработает до истечения токена и успеет открыть список
    подъезда.
    """

    aspirs_ref: str = Field(max_length=64)
    roles: list[ResidentRole] = Field(default_factory=list, max_length=16)


# ── Обход ────────────────────────────────────────────────────────────────────


class RoundEntrance(Strict):
    """Подъезд, назначенный человеку на вечер."""

    building: str = Field(min_length=1, max_length=16)
    entrance: str = Field(min_length=1, max_length=16)
    #: Напарник: обход ходят вдвоём, и человек должен знать, с кем. Подпись для
    #: экрана, а не ключ — открывать по ней чужую карточку обходному незачем.
    partner_name: str | None = Field(default=None, max_length=200)


class RoundAssignment(Strict):
    """Кому какие подъезды в этот вечер.

    Список, а не один подъезд: при нехватке готовых раздача даёт по два, а
    воспитатель ставит и три. Пустой список — снятие с обхода, и работает оно в
    любой момент, в том числе когда состав подъезда человеку уже пришёл.

    Приходит столько раз, сколько воспитатель переигрывает раздачу: она ему
    рекомендация, а не решение. Принимающая сторона заменяет назначение
    целиком, а не дописывает — по той же причине, что и у тегов.
    """

    aspirs_ref: str = Field(max_length=64)
    round_date: date
    entrances: list[RoundEntrance] = Field(default_factory=list, max_length=8)
    #: Часы этого вечера. Перекрывают настройку кабинета, если пришли: сдвинуть
    #: один вечер должно быть можно без правки окружения и рестарта.
    #:
    #: Часа закрытия готовности здесь нет намеренно. Он нужен кабинету с утра, а
    #: это сообщение появляется только после раздачи — взять его отсюда некуда.
    window_opens_at: datetime | None = None
    window_closes_at: datetime | None = None


class RoundPerson(Strict):
    """Жилец подъезда в списке обхода.

    Ровно то, что на экране, и ничего сверх. Расширять на это `profile.updated`
    нельзя: та уходит только на тех, у кого заведён кабинет, а обход идёт по
    всем жильцам — значит пришлось бы слать в ЛКП всю картотеку корпуса с
    контактами ради экрана, которому хватает шести полей.

    Медицинских сведений здесь нет и не будет. `temporary_room` — адрес, и
    только: обходящему нужно знать, где искать человека, а не почему он там.
    """

    aspirs_ref: str = Field(max_length=64)
    last_name: str = Field(min_length=1, max_length=120)
    first_name: str = Field(min_length=1, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    course: int | None = Field(default=None, ge=1, le=9)
    #: Кладёт АСПиРС. Выводить этаж из номера комнаты кабинет не будет: на
    #: первом же корпусе с четырёхзначными номерами это промахнётся молча.
    floor: int | None = Field(default=None, ge=1)
    room: str | None = Field(default=None, max_length=32)
    #: Файл идёт отдельным потоком, здесь только идентификатор.
    photo_id: str | None = Field(default=None, max_length=64)
    #: «Отмечать не нужно» — общая метка, а не «заявление». Человек с ней в счёт
    #: «отмечено N из M» не идёт и кнопок не имеет.
    mark_required: bool = True
    #: Подпись к метке готовой строкой: «Заявление с 8 августа, 17:00 до 10
    #: августа, 20:00». Не причина и не диагноз.
    note: str | None = Field(default=None, max_length=200)
    temporary_room: str | None = Field(default=None, max_length=32)


class RoundRoster(Strict):
    """Состав подъезда на вечер, снимком.

    Живёт своей таблицей и к картотеке кабинета не привязан: обход идёт по всем
    жильцам, включая тех, кто кабинет не заводил.
    """

    round_date: date
    building: str = Field(min_length=1, max_length=16)
    entrance: str = Field(min_length=1, max_length=16)
    people: list[RoundPerson] = Field(default_factory=list, max_length=MAX_ROUND_PEOPLE)


class RoundSchedule(Strict):
    """Часы вечера. Уходит при каждой правке настроек обхода.

    Заведено 12.08.2026, когда часы в АСПиРС переехали из окружения в базу и
    стали редактируемыми с экрана воспитателя. До этого обе системы держали их
    настройкой, и сдвиг вечера был симметричной ручной работой с обеих сторон.

    Час открытия и закрытия кабинет и так узнаёт из `round.assignment`, но
    **час закрытия готовности оттуда узнать нельзя**: назначение появляется уже
    после него. Без этого сообщения воспитатель сдвигает готовность у себя, а
    кабинет продолжает принимать «иду сегодня» по старому часу — то есть
    принимает отметку, которая в раздачу уже не попадёт, и показывает студенту
    час, которого нет. Отказ беззвучный с обеих сторон: у одного зелёный экран,
    у другого «я же отметился».

    Едет полное расписание, а не изменённое поле: набор из трёх часов
    самоисправляется, а приращение требует, чтобы обе стороны одинаково считали
    порядок сообщений.

    Глубины истории раздач здесь нет намеренно: ротация живёт в АСПиРС целиком,
    и кабинету это число нечем применить. В контракт попадает то, что
    принимающая сторона показывает или проверяет, а не всё, что у отправителя
    лежит в одной таблице.
    """

    #: Время суток во времени кампуса, без зоны: «21:00». Не момент — часы
    #: действуют каждый вечер, пока их снова не поменяют.
    readiness_closes_time: time
    opens_time: time
    closes_time: time


class RoundExtended(Strict):
    """Ночной продлил один подъезд, а не вечер целиком.

    Двигать вечер всем ради одного незакрытого значило бы снова открыть уже
    сданные подъезды. По истечении продления подъезд закрывается тем же
    порядком, что и в общий час.
    """

    round_date: date
    building: str = Field(min_length=1, max_length=16)
    entrance: str = Field(min_length=1, max_length=16)
    closes_at: datetime
    #: Подпись сотрудника для экрана: обходной должен видеть, что продление
    #: настоящее, а не показалось.
    extended_by: str | None = Field(default=None, max_length=200)


# ── Служебное ────────────────────────────────────────────────────────────────


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
    "home.layout": HomeLayout,
    "profile.updated": ProfileUpdated,
    "ticket.status_changed": TicketStatusChanged,
    "leave.status_changed": ApplicationStatusChanged,
    "pass.status_changed": ApplicationStatusChanged,
    "linen.granted": LinenGranted,
    "linen.debt_created": LinenDebtCreated,
    "account.invited": AccountInvited,
    "account.blocked": AccountBlocked,
    "account.unblocked": AccountBlocked,
    "account.roles_updated": AccountRolesUpdated,
    "round.assignment": RoundAssignment,
    "round.roster": RoundRoster,
    "round.schedule": RoundSchedule,
    "round.extended": RoundExtended,
    "message.stored": MessageStored,
}
