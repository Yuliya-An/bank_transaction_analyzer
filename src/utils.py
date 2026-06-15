import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from collections import defaultdict

CASHBACK_RATES = {
    "Супермаркеты": 0.05,
    "Аптеки": 0.10,
    "Транспорт": 0.01,
    "Прочее": 0.01,
}


def read_operations_from_json(filepath: str) -> list[dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def read_operations_from_csv(filepath: str) -> list[dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        return [row for row in reader]


def read_operations_from_xlsx(filepath: str) -> list[dict[str, Any]]:
    import pandas as pd

    df = pd.read_excel(filepath)
    df = df.fillna("")
    if "Дата операции" in df.columns:
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], dayfirst=True
        ).dt.strftime("%Y-%m-%d")
    mapping = {
        "Дата операции": "date",
        "Сумма платежа": "amount",
        "Категория": "category",
        "Описание": "description",
        "Номер карты": "card",
        "Кешбэк": "cashback",
    }
    df = df.rename(columns=mapping)
    return df.to_dict(orient="records")


def get_greeting_by_time() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def read_data(data_dir: Any) -> list[dict[str, Any]]:
    data_dir = Path(data_dir)
    if data_dir.suffix == '.xlsx':
        path = data_dir
    else:
        path = data_dir / "operations.xlsx"

    if path.exists():
        try:
            return read_operations_from_xlsx(str(path))
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
    else:
        # Вместо пустого списка возвращаем заглушку, если нужно для тестов,
        # но здесь оставим пустой список и поправим сам тест позже.
        print(f"ФАЙЛ НЕ НАЙДЕН ПО ПУТИ: {path.absolute()}")
    return []


def search_transactions(data: list, query: str) -> list:
    if not query:
        return []
    results = []
    query_lower = query.lower()
    for t in data:
        # Собираем всё в одну строку, гарантируя, что всё это строки (str)
        text = f"{str(t.get('description', ''))} {str(t.get('category', ''))} {str(t.get('card', ''))}".lower()
        if query_lower in text:
            results.append(t)
    return results


def calculate_investment_savings(data: list, limit: int = 100) -> float:
    total_saved = 0.0
    for t in data:
        try:
            amount = float(t.get("amount", 0))
            if amount < 0:
                val = abs(amount)
                # Считаем остаток до ближайшего десятка
                remainder = val % 10
                if remainder != 0:
                    total_saved += (10 - remainder)
        except (ValueError, TypeError):
            continue
    return round(total_saved, 2)


def analyze_cashback_categories(data: list, year: int, month: int) -> dict:
    monthly_data = []
    for t in data:
        try:
            dt = datetime.strptime(t.get("date", "2000-01-01"), "%Y-%m-%d")
            if dt.year == year and dt.month == month:
                monthly_data.append(t)
        except (ValueError, TypeError):
            continue

    cashback_total = 0.0
    for t in monthly_data:
        cat = t.get("category", "Прочее")
        amount = abs(float(t.get("amount", 0)))
        cashback_total += amount * CASHBACK_RATES.get(cat, CASHBACK_RATES["Прочее"])

    return {"total_cashback": round(cashback_total, 2), "count": len(monthly_data)}


def get_best_cashback_categories(data: list, year: int, month: int) -> list:
    monthly_data = []
    for t in data:
        try:
            dt = datetime.strptime(t.get("date", "2000-01-01"), "%Y-%m-%d")
            if dt.year == year and dt.month == month:
                monthly_data.append(t)
        except (ValueError, TypeError):
            continue

    cat_sums = defaultdict(float)
    for t in monthly_data:
        cat = t.get("category", "Прочее")
        amount = abs(float(t.get("amount", 0)))
        cat_sums[cat] += amount * CASHBACK_RATES.get(cat, CASHBACK_RATES["Прочее"])

    return sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)


def get_events_page(data: list[dict[str, Any]], period: str) -> dict[str, Any]:
    now = datetime.now()
    if period == "W":
        cutoff = now - timedelta(days=7)
    elif period == "M":
        cutoff = now - timedelta(days=30)
    elif period == "Y":
        cutoff = now - timedelta(days=365)
    else:
        cutoff = datetime(2000, 1, 1)

    filtered = []
    for t in data:
        try:
            date_val = datetime.strptime(t.get("date", "2000-01-01"), "%Y-%m-%d")
            if date_val >= cutoff:
                filtered.append(t)
        except (ValueError, TypeError):
            continue

    categories = {}
    total_income = 0.0
    total_expense = 0.0
    for t in filtered:
        cat = t.get("category", "Другое")
        try:
            amount = float(t.get("amount", 0))
            if amount > 0:
                total_income += amount
            else:
                total_expense += abs(amount)
            categories[cat] = categories.get(cat, 0) + amount
        except (ValueError, TypeError):
            continue

    rounded_categories = {k: round(v, 2) for k, v in categories.items()}
    sorted_categories = dict(sorted(rounded_categories.items(), key=lambda x: x[1], reverse=True))

    return {
        "period": period,
        "income": round(total_income, 2),
        "expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2),
        "categories": sorted_categories,
        "count": len(filtered)
    }


def get_analysis_page(data: list, query: str = None, year: int = None, month: int = None) -> dict:
    res = {}
    if query:
        res["search"] = search_transactions(data, query)
    res["savings"] = calculate_investment_savings(data)
    if year and month:
        res["best_cats"] = get_best_cashback_categories(data, year, month)
        res["cashback_report"] = analyze_cashback_categories(data, year, month)
    return res
