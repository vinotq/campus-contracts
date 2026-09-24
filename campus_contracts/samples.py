"""По одному годному телу на каждый тип.

Нужны здесь, а не в тестах: этими же образцами проверяются отправители в АСПиРС
и в кабинете. Один набор на три репозитория — иначе каждая сторона придумает
себе свой пример, и они разойдутся так же, как разошлись схемы.
"""

from campus_contracts import Direction

DOWNSTREAM = {
    "news.published": {
        "aspirs_ref": "412",
        "kind": "news",
        "title": "Субботник во дворе",
        "body_md": "Собираемся в субботу в 11 у восьмого корпуса.",
        "rubric": "Двор",
        "rubrics": ["Двор", "Важно"],
        "author_label": "Воспитатели корпуса 8",
        "is_urgent": False,
        "published_at": "2026-08-04T12:00:00+03:00",
        "audience": {"buildings": ["8", "9"], "courses": [1, 2], "groups": []},
        "image_ids": ["1841", "1842"],
    },
    "news.updated": {
        "aspirs_ref": "412",
        "kind": "news",
        "title": "Субботник во дворе перенесён",
        "body_md": "Не в субботу, а в воскресенье, время прежнее.",
        "published_at": "2026-08-04T12:00:00+03:00",
    },
    "news.deleted": {"aspirs_ref": "412"},
    "event.published": {
        "aspirs_ref": "413",
        "kind": "event",
        "title": "Встреча с выпускниками",
        "body_md": "В актовом зале.",
        "published_at": "2026-08-05T09:00:00+03:00",
    },
    "event.updated": {
        "aspirs_ref": "413",
        "kind": "event",
        "title": "Встреча с выпускниками",
        "body_md": "В актовом зале, вход свободный.",
        "published_at": "2026-08-05T09:00:00+03:00",
    },
    "notice.urgent": {"aspirs_ref": "414", "title": "Отключение горячей воды до 18:00"},
    "home.layout": {
        "blocks": [
            {"key": "greeting", "kind": "greeting", "sort_order": 0},
            {"key": "movement", "kind": "movement", "sort_order": 1},
            {"key": "news", "kind": "news", "title": "Новости", "sort_order": 2},
            {
                "key": "17",
                "kind": "custom",
                "title": "Ремонт лифта",
                "body_md": "Левый лифт восьмого корпуса стоит до пятницы.",
                "link_url": "/reference/rules",
                "link_label": "Правила проживания",
                "sort_order": 3,
            },
        ]
    },
    "profile.updated": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "last_name": "Демидов",
        "first_name": "Глеб",
        "middle_name": "Иванович",
        "course": None,
        "study_group": "К0709-23/1",
        "building": "12",
        "entrance": "1",
        "room": "101",
        "birth_date": "2004-01-20",
        "is_adult": True,
        "residency_status": "living",
        "phone": "79001234567",
        "email": "gleb.demidov@mail.ru",
        "telegram": "@gleb",
        "vk": None,
        "notice": "Пригласите завтра к Воспитателям с 9:00 до 21:00",
    },
    "ticket.status_changed": {
        "ticket_ref": "018f2c5e-0000-7000-8000-000000000001",
        "item_ref": "018f2c5e-0000-7000-8000-000000000002",
        "status": "in_progress",
        "note": "Сантехник придёт после обеда",
    },
    "leave.status_changed": {
        "application_ref": "018f2c5e-0000-7000-8000-000000000003",
        "status": "with_tutor",
    },
    "pass.status_changed": {
        "application_ref": "018f2c5e-0000-7000-8000-000000000004",
        "status": "declined",
        "decline_reason": "Даты выходят за срок проживания",
    },
    "linen.granted": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-08-03",
        "granted_at": "2026-08-05T10:15:00+03:00",
        "method": "qr",
        "granted_by": "Кастелянша корпуса 12",
    },
    "linen.debt_created": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-07-27",
    },
    "account.invited": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "code_hash": "9f" * 32,
        "expires_at": "2026-08-12T10:00:00+03:00",
        "purpose": "activation",
    },
    "account.blocked": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "reason": "Обратитесь к воспитателям",
    },
    "account.unblocked": {"aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv"},
    "scanner.updated": {
        "login": "prachka",
        "name": "Прачечная",
        "active": True,
        "password_hash": "$argon2id$v=19$m=19456,t=2,p=1$c2FsdHNhbHQ$aGFzaGhhc2hoYXNoaGFzaA",
    },
    "account.roles_updated": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "roles": ["rounds"],
    },
    "round.assignment": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "round_date": "2026-08-12",
        "entrances": [
            {"building": "8", "entrance": "2", "partner_name": "Соколова Мария"},
        ],
        "window_opens_at": "2026-08-12T21:59:00+03:00",
        "window_closes_at": "2026-08-12T23:00:00+03:00",
        "rounds_walked": 17,
    },
    "round.roster": {
        "round_date": "2026-08-12",
        "building": "8",
        "entrance": "2",
        "people": [
            {
                "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
                "last_name": "Демидов",
                "first_name": "Глеб",
                "middle_name": "Иванович",
                "course": 2,
                "floor": 3,
                "room": "312",
                "photo_id": "018f2c5e-0000-7000-8000-00000000000c",
                "mark_required": True,
                "note": None,
                "temporary_room": None,
                # Сегодня восемнадцать: в списке до конца вечера, назавтра его
                # тут не будет.
                "flags": ["adult_today"],
            },
            {
                "aspirs_ref": "Qw3_r7TfGh0LmN2pQrStUv",
                "last_name": "Соколова",
                "first_name": "Мария",
                "middle_name": None,
                "course": 1,
                "floor": 3,
                "room": "315",
                "photo_id": None,
                "mark_required": False,
                "note": "Заявление с 8 августа, 17:00 до 10 августа, 20:00",
                "temporary_room": "8-1-5333",
            },
        ],
    },
    "round.schedule": {
        "readiness_closes_time": "21:00",
        "opens_time": "21:59",
        "closes_time": "23:00",
    },
    "round.extended": {
        "round_date": "2026-08-12",
        "building": "8",
        "entrance": "2",
        "closes_at": "2026-08-13T00:30:00+03:00",
        "extended_by": "Ночной воспитатель корпуса 8",
    },
    "message.stored": {"message_id": "018f2c5e-0000-7000-8000-000000000005"},
}

UPSTREAM = {
    "ticket.created": {
        "ticket_ref": "018f2c5e-0000-7000-8000-000000000001",
        "number": "Р-25-802",
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "place": "room",
        "place_note": "Кухня блока, дальняя раковина",
        "items": [
            {
                "ref": "018f2c5e-0000-7000-8000-000000000002",
                "position": 1,
                "text": "Течёт смеситель",
                "is_urgent": False,
                "photos": ["018f2c5e-0000-7000-8000-00000000000a"],
            }
        ],
    },
    "ticket.item_added": {
        "ticket_ref": "018f2c5e-0000-7000-8000-000000000001",
        "item": {
            "ref": "018f2c5e-0000-7000-8000-000000000006",
            "position": 2,
            "text": "И розетка искрит",
            "is_urgent": True,
            "photos": [],
        },
    },
    "ticket.withdrawn": {"ticket_ref": "018f2c5e-0000-7000-8000-000000000001"},
    "leave.submitted": {
        "application_ref": "018f2c5e-0000-7000-8000-000000000003",
        "number": "В-25-145",
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "from_at": "2026-08-15T18:00:00+03:00",
        "to_at": "2026-08-17T21:00:00+03:00",
        "reason": "Домой к родителям",
        "scan": "018f2c5e-0000-7000-8000-00000000000b",
        "voice_in_chat": False,
    },
    "pass.submitted": {
        "application_ref": "018f2c5e-0000-7000-8000-000000000004",
        "number": "П-25-67",
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "from_date": "2026-08-20",
        "to_date": "2026-08-21",
        "from_time": "14:00:00",
        "to_time": "12:00:00",
        "visitors": [
            {
                "position": 1,
                "fio": "Демидова Ольга Петровна",
                "relation": "мать",
                "document": "4519 123456",
            }
        ],
        "cars": [{"make": "Lada Vesta", "plate": "А123ВС777"}],
    },
    "application.withdrawn": {"application_ref": "018f2c5e-0000-7000-8000-000000000003"},
    "linen.debt_acknowledged": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-07-27",
    },
    "linen.collected": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-09-20",
        "collected_at": "2026-09-20T10:15:00+03:00",
        "by_proxy": True,
        "station": "Прачечная",
    },
    "device.registered": {"aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv"},
    "round.readiness": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "round_date": "2026-08-12",
        "ready": True,
    },
    "round.submitted": {
        "round_date": "2026-08-12",
        "building": "8",
        "entrance": "2",
        "submitted_by": "Zx8_q1TfGh0LmN2pQrStUv",
        "submitted_at": "2026-08-12T22:40:00+03:00",
        "auto_closed": False,
        "marks": [
            {
                "aspirs_ref": "Qw3_r7TfGh0LmN2pQrStUv",
                "mark": "present",
                "comment": None,
                "marked_by": "Zx8_q1TfGh0LmN2pQrStUv",
            },
            {
                "aspirs_ref": "Ty5_k2TfGh0LmN2pQrStUv",
                "mark": "absent",
                "comment": "Сказали, уехал к родителям",
                "marked_by": "Zx8_q1TfGh0LmN2pQrStUv",
            },
            {
                "aspirs_ref": "Uu9_m4TfGh0LmN2pQrStUv",
                "mark": "unmarked",
                "comment": None,
                "marked_by": None,
            },
        ],
    },
}

SAMPLES = {
    Direction.DOWNSTREAM: DOWNSTREAM,
    Direction.UPSTREAM: UPSTREAM,
}
