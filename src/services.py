import re
from typing import Any, Dict, List


def analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """Анализ кешбэка по категориям за указанный месяц."""
    rates = {"Супермаркеты": 0.05, "Аптеки": 0.10, "Транспорт": 0.05}

    monthly_transactions = filter(
        lambda t: t.get("date", "").startswith(f"{year}-{month:02d}") and float(t.get("amount", 0)) < 0,
        data
    )

    result = {}
    for t in monthly_transactions:
        cat = t.get("category", "Другое")
        amount = abs(float(t.get("amount", 0)))
        rate = rates.get(cat, 0.01)
        result[cat] = result.get(cat, 0) + amount * rate

    return result


def search_transactions(data: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Универсальный поиск: обычный, по телефону, по переводам физлицам."""
    query_lower = query.lower()
    results = []

    # Безопасная проверка на телефон
    is_phone_query = len(query.strip()) >= 5 and all(c.isdigit() or c in ' \t\n\r\f\v()+-' for c in query.strip())

    # Компилируем паттерн телефона: ищем 11 цифр, начинающихся с 7 или 8.
    # Этот вариант работает после очистки строки от не-цифр (re.sub(r'\D', '', desc)),
    # поэтому ловит и '+7 999 123-45-67', и '8-800-555-35-35', и другие форматы.
    phone_pattern = re.compile(r'[78]\d{10}')

    # Проверка на переводы
    transfer_keywords = ["перевод", "перечисление", "физлицо", "физическое лицо"]
    is_transfer_query = any(kw in query_lower for kw in transfer_keywords)

    for t in data:
        desc = str(t.get("description", "")).lower()

        if is_phone_query:
            # Убираем все не-цифры из описания для поиска — это приводит номер к единому виду
            clean_desc = re.sub(r'\D', '', desc)
            if phone_pattern.search(clean_desc):
                results.append(t)
            continue

        if is_transfer_query:
            transfer_pattern = re.compile(
                r'(перевод\s+(на\s+)?карту|перевод\s+физлицу|перевод\s+физическому\s+лицу|'
                r'перевод\s+[а-яё]+\s+[а-яё]+)',
                re.IGNORECASE
            )
            if transfer_pattern.search(desc):
                results.append(t)
            continue

        if query_lower in desc:
            results.append(t)

    return results


def calculate_investment_savings(data: List[Dict[str, Any]], limit: int = 100) -> float:
    """Инвесткопилка: округление расходов до лимита."""
    # Используем sum, map и lambda для функционального стиля
    total = sum(
        map(
            lambda t: abs(float(t.get("amount", 0))) % limit,
            filter(lambda t: float(t.get("amount", 0)) < 0, data)
        )
    )
    return round(total, 2)


def get_best_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> List[tuple]:
    """Возвращает топ-3 категорий с наибольшим кэшбэком."""
    analysis = analyze_cashback_categories(data, year, month)
    return sorted(analysis.items(), key=lambda x: x[1], reverse=True)[:3]


def get_currency_rates(currencies: list) -> dict:
    """Заглушка для получения курсов валют."""
    return {}


def get_stock_prices(stocks: list) -> list:
    """Заглушка для получения цен акций."""
    return []
