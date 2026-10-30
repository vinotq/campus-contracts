"""Словари значений.

Всё перечислимое, что ходит по каналу, живёт здесь и только здесь. Свободных
строк среди статусов быть не должно: разошедшийся словарь ломается тише
разошедшегося имени поля — сообщение принимается, а на экране появляется статус,
которого никто не рисовал.
"""

from enum import StrEnum


class ApplicationStatus(StrEnum):
    """Статус заявления на выход и пропуска для родных.

    Четыре состояния и отзыв. Стадии «проверены документы» нет намеренно:
    комендатура её не ведёт, а показывать студенту движение, которого не
    происходит, хуже, чем не показывать ничего.
    """

    #: Заявление ушло, АСПиРС ещё не подтвердил приём.
    SUBMITTED = "submitted"
    #: В работе у воспитателя. Внутри АСПиРС это `pending`.
    WITH_TUTOR = "with_tutor"
    APPROVED = "approved"
    #: Внутри АСПиРС это `rejected`. Причина обязательна.
    DECLINED = "declined"
    #: Студент отозвал сам.
    WITHDRAWN = "withdrawn"


APPLICATION_STATUS_LABELS = {
    ApplicationStatus.SUBMITTED: "Отправлено",
    ApplicationStatus.WITH_TUTOR: "Взято в работу",
    ApplicationStatus.APPROVED: "Одобрено",
    ApplicationStatus.DECLINED: "Отклонено",
    ApplicationStatus.WITHDRAWN: "Отозвано",
}


class TicketSpot(StrEnum):
    COWORKING = "coworking"
    KITCHEN = "kitchen"
    LAUNDRY = "laundry"
    SHOWER = "shower"
    TOILET = "toilet"
    CORRIDOR = "corridor"
    LIFT = "lift"
    STAIRS = "stairs"
    YARD_8_9 = "yard_8_9"
    YARD_11_12 = "yard_11_12"


TICKET_SPOT_LABELS = {
    TicketSpot.COWORKING: "коворкинг",
    TicketSpot.KITCHEN: "кухня",
    TicketSpot.LAUNDRY: "прачечная",
    TicketSpot.SHOWER: "душевая",
    TicketSpot.TOILET: "санузел",
    TicketSpot.CORRIDOR: "коридор",
    TicketSpot.LIFT: "лифт",
    TicketSpot.STAIRS: "лестничный марш",
    TicketSpot.YARD_8_9: "двор между 8 и 9 корпусами",
    TicketSpot.YARD_11_12: "двор между 11 и 12 корпусами",
}

TICKET_SPOT_CHOICES = (
    TicketSpot.COWORKING,
    TicketSpot.KITCHEN,
    TicketSpot.LAUNDRY,
    TicketSpot.TOILET,
    TicketSpot.CORRIDOR,
    TicketSpot.LIFT,
    TicketSpot.STAIRS,
    TicketSpot.YARD_8_9,
    TicketSpot.YARD_11_12,
)


class ItemStatus(StrEnum):
    """Статус позиции в заявке на ремонт.

    У АСПиРС внутри `in_work`, здесь `in_progress`: одно слово, но выбрать
    надо одно. Перевод делается на границе, таблицы не трогаются.

    Стадии «Принято» больше нет (решено 11.08.2026): между «Отправлена» и «В
    работе» ничего не происходило, и студент видел движение там, где его не
    было. Слесарь либо ещё не взялся, либо уже чинит.
    """

    SENT = "sent"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    #: Причина обязательна.
    REJECTED = "rejected"


ITEM_STATUS_LABELS = {
    ItemStatus.SENT: "Отправлена",
    ItemStatus.IN_PROGRESS: "В работе",
    ItemStatus.DONE: "Выполнена",
    ItemStatus.REJECTED: "Отклонена",
}


class PostKind(StrEnum):
    """Вид публикации.

    С 1.23.0 АСПиРС шлёт только `news` и `reference`: место и время может
    иметь любая новость (поле `event`). `event` остаётся для приёма от АСПиРС
    до 1.23.0. Записи на события в контракте нет.
    """

    NEWS = "news"
    EVENT = "event"
    #: Правила, контакты дежурных, часто задаваемое. Живёт в справочной.
    REFERENCE = "reference"


class HomeBlockKind(StrEnum):
    """Блок главной кабинета.

    Штатные блоки собирает сам кабинет из своих же данных: приветствие знает
    имя, движение по заявлению — заявления, полки справочной — публикации.
    АСПиРС говорит только, показывать ли их, в каком порядке и под каким
    заголовком. Своё содержимое есть лишь у `custom`.
    """

    GREETING = "greeting"
    #: Движение по заявлению: где сейчас поданное на выход.
    MOVEMENT = "movement"
    NOTIFICATIONS = "notifications"
    NEWS = "news"
    #: Полка «Частые вопросы» и полка «Правила и справочники».
    FAQ = "faq"
    REFERENCE = "reference"
    #: Блок, написанный в АСПиРС: заголовок, текст и одна ссылка.
    CUSTOM = "custom"


class LinenMethod(StrEnum):
    """Как выдали бельё. У АСПиРС поле называется `way`."""

    QR = "qr"
    MANUAL = "manual"


class CodePurpose(StrEnum):
    """Зачем выдан одноразовый код.

    Восстановление пароля идёт тем же механизмом, что и активация:
    самообслуживания по почте нет.
    """

    ACTIVATION = "activation"
    RESET = "reset"


class ResidencyStatus(StrEnum):
    LIVING = "living"
    EVICTED = "evicted"


class ProfileField(StrEnum):
    """Что студент может попросить поправить в карточке. Фото меняют только воспитатели."""

    TELEGRAM = "telegram"
    VK = "vk"
    PHONE = "phone"
    BIRTH_DATE = "birth_date"
    EMAIL = "email"
    ROOM = "room"


class ResidentRole(StrEnum):
    """Тег студента: чем он занят сверх проживания.

    Открыт на пополнение. Заводится строкой здесь и попадает в обе системы
    вместе с версией пакета — без миграций и без правки схем: набор тегов
    едет списком, а не колонкой на каждый.

    Мастер тегов — АСПиРС. ЛКП их не выдаёт и не отзывает, только принимает.

    **Тег сам по себе кабинета не открывает.** Что он там даёт, решает
    принимающая сторона: у ЛКП это карта `roles.OPENS`, и тега, которого в ней
    нет, для кабинета не существует — ни разделом, ни входом. Новый ключ здесь
    поэтому безопасен: до выкладки кабинета он ничего не открывает, а не
    открывает всё.
    """

    #: Обходной: ходит по подъезду и отмечает, кто на месте.
    ROUNDS = "rounds"
    #: Медиа: снимает и пишет про жизнь кампуса. Ручек обхода не открывает.
    MEDIA = "media"
    HEADMAN = "headman"
    #: Волонтёр, с 1.23.0: АСПиРС ведёт ему волонтёрские часы.
    VOLUNTEER = "volunteer"
    DUTY_ALL = "duty_all"
    ROUNDS_ALL = "rounds_all"
    POSTS_ALL = "posts_all"
    MEDIA_REVIEW = "media_review"


RESIDENT_RIGHTS = (
    ResidentRole.DUTY_ALL,
    ResidentRole.ROUNDS_ALL,
    ResidentRole.POSTS_ALL,
    ResidentRole.MEDIA_REVIEW,
)


class MediaRequestStatus(StrEnum):
    SENT = "sent"
    IN_WORK = "in_work"
    READY = "ready"
    PUBLISHED = "published"


class PostVerdict(StrEnum):
    APPROVED = "approved"
    REWORK = "rework"


class RoundMark(StrEnum):
    """Отметка по человеку в обходе.

    Состояний три, а не два. Неотправленный обход уходит из кабинета сам в
    конце вечера, и те, до кого обходной не дошёл, едут третьим состоянием:
    «не отмечен» — это не «нет на месте», и путать их нельзя.
    """

    PRESENT = "present"
    ABSENT = "absent"
    UNMARKED = "unmarked"


class PersonFlag(StrEnum):
    """Пометка к человеку в списке обхода.

    Списком, а не булевым полем на каждый случай: такие пометки будут
    появляться, и заводить под каждую свою колонку значит переделывать контракт,
    схемы и таблицы по третьему разу. Список из словаря — новое значение
    добавляется строкой здесь, старые не трогаются.

    Значения перечислимые, свободных строк среди них нет: пометка попадает на
    экран рядом с чужим именем, и «что-нибудь придумает отправитель» здесь
    ровно то, чего контракт не допускает.

    Подпись пишет принимающая сторона. Отправитель сообщает **факт**, а не
    формулировку: у кабинета «сегодня 18 — последний обход», у другого клиента
    когда-нибудь будет своя.
    """

    #: Сегодня человеку исполнилось восемнадцать. Формально он уже взрослый и
    #: обходу не подлежит, но вечер тот же: пропади он молча, воспитатель пойдёт
    #: искать ребёнка, которого в списке больше нет. Назавтра пометки не будет,
    #: как и человека.
    ADULT_TODAY = "adult_today"
