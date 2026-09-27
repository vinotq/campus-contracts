from pydantic import Field, field_validator

from campus_contracts.envelope import Strict

MAX_DUTY_ZONES = 8
MAX_DUTY_ZONE_ITEMS = 8
MAX_DUTY_ITEM_LENGTH = 120


class DutyZone(Strict):
    name: str = Field(min_length=1, max_length=40)
    items: list[str] = Field(min_length=1, max_length=MAX_DUTY_ZONE_ITEMS)

    @field_validator("items")
    @classmethod
    def _items(cls, value: list[str]) -> list[str]:
        if any(not item.strip() or len(item) > MAX_DUTY_ITEM_LENGTH for item in value):
            raise ValueError(f"пункт от 1 до {MAX_DUTY_ITEM_LENGTH} символов")
        return value


DEFAULT_INSTRUCTION: list[dict] = [
    {
        "name": "Кухня",
        "items": [
            "Протереть столы, столешницы, плиту и раковину",
            "Проверить, что микроволновка чистая, и оставить её открытой для проветривания",
            "Проверить, что пол чистый",
        ],
    },
    {
        "name": "Постирочная",
        "items": [
            "Выгрузить постиранное и посушенное белье из стиральных и сушильных машин",
            "Очистить сборники воды и ворса в сушильных машинах",
            "Навести порядок в помещении",
            "Напомнить в чате подъезда забрать вещи из стирки и сушки",
        ],
    },
    {
        "name": "Гладильные доски",
        "items": [
            "На каждом этаже есть доска и утюг",
            "Покрытие доски чистое",
            "Утюг выключен, на подошве чехол",
        ],
    },
    {
        "name": "Коворкинги",
        "items": ["Убрать мусор", "Расставить мебель по местам"],
    },
    {
        "name": "Лифт",
        "items": ["Проверить, что в кабине чисто"],
    },
    {
        "name": "Фотоотчёт",
        "items": ["Сфотографировать каждую локацию после проверки", "Отправить фото старосте"],
    },
]
