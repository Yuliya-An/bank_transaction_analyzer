from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from src import services


def safe_date(tx: Dict[str, Any]) -> datetime:
    """Преобразует дату из строки в объект datetime, чтобы сортировка не упала."""
    try:
        return datetime.strptime(tx.get("date", "0001-01-01"), "%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime(1, 1, 1)


def get_main_page(data: List[Dict[str, Any]], settings: Dict[str, Any]) -> Dict[str, Any]:
    # Сортируем по дате (свежие сверху), используя наш предохранитель safe_date
    sorted_data = sorted(data, key=safe_date, reverse=True)
    recent_activity = sorted_data[:5]

    # Считаем общий баланс
    total_balance = sum(t.get("amount", 0) for t in data)

    # Получаем данные из сервисов (теперь они не упадут благодаря заглушкам)
    currencies = services.get_currency_rates(settings.get("currencies", []))
    stocks = services.get_stock_prices(settings.get("stocks", []))

    return {
        "greeting": f"Здравствуйте, {settings.get('user_name', 'Пользователь')}!",
        "balance": float(total_balance),
        "cards": settings.get("cards", []),
        "recent_activity": recent_activity,
        "currency_rates": currencies,
        "stock_prices": stocks,
    }


def get_events_page(data: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
    now = datetime.now()
    if period == "W":
        cutoff_date = now - timedelta(days=7)
    elif period == "M":
        cutoff_date = now - timedelta(days=30)
    elif period == "Y":
        cutoff_date = now - timedelta(days=365)
    else:  # ALL или любой другой период
        cutoff_date = datetime.min

    filtered_data = []
    for t in data:
        try:
            if datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff_date:
                filtered_data.append(t)
        except (ValueError, KeyError):
            continue

    category_totals = defaultdict(float)
    for t in filtered_data:
        category_totals[t["category"]] += t["amount"]

    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_7 = sorted_cats[:7]
    others = sorted_cats[7:]

    final_breakdown = {k: round(v, 2) for k, v in top_7}
    if others:
        others_sum = sum(v for k, v in others)
        final_breakdown["Остальное"] = round(others_sum, 2)

    return {
        "period": period,
        "total_sum": round(sum(t.get("amount", 0) for t in filtered_data), 2),
        "breakdown": final_breakdown,
        "count": len(filtered_data),
    }


def get_analysis_page(data: List[Dict[str, Any]], year: int = None, month: int = None, query: str = None) -> Dict[str, Any]:
    result = {}

    # Если задан поисковый запрос
    if query:
        from src.services import search_transactions
        result["search_results"] = search_transactions(data, query)

    # Если заданы год и месяц — делаем глубокий анализ
    if year and month:
        from src.services import analyze_cashback_categories, get_best_cashback_categories
        # Фильтруем данные по году и месяцу
        filtered_data = [
            t for t in data
            if t.get("date", "").startswith(f"{year}-{month:02d}")
        ]
        # Передаем данные, год и месяц!
        result["cashback_report"] = analyze_cashback_categories(filtered_data, year, month)
        result["best_categories"] = get_best_cashback_categories(filtered_data, year, month)

    # Инвесткопилка считается всегда
    from src.services import calculate_investment_savings
    result["investment_savings"] = calculate_investment_savings(data)

    return result
