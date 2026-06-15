import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

CATEGORIES = [
    "Супермаркеты", "Фастфуд", "Топливо", "Развлечения",
    "Медицина", "Переводы", "Наличные", "ЖКХ", "Бонусы",
    "Пополнение_BANK007", "Проценты_на_остаток", "Кэшбэк"
]

CARDS = ["5814", "7512"]

DESCRIPTIONS = [
    "Лента", "Пятёрочка", "Яндекс.Еда", "KFC", "Лукойл",
    "Тинькофф Мобайл +7 995 555-55-55", "Я МТС +7 921 11-22-33",
    "Валерий А.", "Сергей З.", "Артем П.", "Ozon.ru",
    "ЖКУ Квартира", "Кешбэк за обычные покупки", "Авито",
    "Перевод Кредитная карта. ТП 10.2 RUR"
]


def generate_transactions():
    transactions = []
    start_date = datetime(2023, 1, 1)

    for i in range(200):
        date = start_date + timedelta(days=random.randint(0, 500))
        category = random.choice(CATEGORIES)
        amount = round(random.uniform(-15000, 30000), 2)
        card = random.choice(CARDS)
        description = random.choice(DESCRIPTIONS)

        transactions.append({
            "date": date.strftime("%Y-%m-%d"),
            "amount": amount,
            "category": category,
            "description": description,
            "card": card
        })

    return transactions


def save_data():
    DATA_DIR.mkdir(exist_ok=True)

    data = generate_transactions()

    with open(DATA_DIR / "operations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Данные успешно сгенерированы в папке data!")


if __name__ == "__main__":
    save_data()
