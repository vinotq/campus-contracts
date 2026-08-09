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
        "author_label": "Комендатура корпуса 8",
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
    "linen.entitlement_changed": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-08-03",
        "entitled": True,
    },
    "linen.granted": {
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "period_start": "2026-08-03",
        "granted_at": "2026-08-05T10:15:00+03:00",
        "method": "qr",
        "granted_by": "Комендатура корпуса 12",
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
        "reason": "Обратитесь к коменданту корпуса",
    },
    "account.unblocked": {"aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv"},
    "message.stored": {"message_id": "018f2c5e-0000-7000-8000-000000000005"},
}

UPSTREAM = {
    "ticket.created": {
        "ticket_ref": "018f2c5e-0000-7000-8000-000000000001",
        "number": "Р-1204",
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
        "number": "В-318",
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "from_at": "2026-08-15T18:00:00+03:00",
        "to_at": "2026-08-17T21:00:00+03:00",
        "reason": "Домой к родителям",
        "scan": "018f2c5e-0000-7000-8000-00000000000b",
        "voice_in_chat": False,
    },
    "pass.submitted": {
        "application_ref": "018f2c5e-0000-7000-8000-000000000004",
        "number": "П-77",
        "aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv",
        "from_date": "2026-08-20",
        "to_date": "2026-08-21",
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
    "device.registered": {"aspirs_ref": "Zx8_q1TfGh0LmN2pQrStUv"},
}

SAMPLES = {
    Direction.DOWNSTREAM: DOWNSTREAM,
    Direction.UPSTREAM: UPSTREAM,
}
