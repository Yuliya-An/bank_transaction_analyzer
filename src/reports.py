import json
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, List, Dict


def report(output_dir: str = "reports") -> Callable:
    """Декоратор для автоматического сохранения результата функции в JSON-файл."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/{func.__name__}_{timestamp}.json"
            os.makedirs(output_dir, exist_ok=True)
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Ошибка при записи отчета: {e}")
            return result

        return wrapper

    return decorator


@report()
def generate_spending_report(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Отчет по тратам по категориям. Только расходы, округлено до целых, отсортировано."""
    category_totals = {}
    for t in transactions:
        cat = t.get("category", "Прочее")
        amount = float(t.get("amount", 0))
        if amount < 0:  # Только расходы
            category_totals[cat] = category_totals.get(cat, 0) + abs(amount)

    # Округляем до целых
    rounded_totals = {cat: round(total) for cat, total in category_totals.items()}

    # Сортируем по убыванию суммы
    sorted_breakdown = dict(sorted(rounded_totals.items(), key=lambda x: x[1], reverse=True))

    return {
        "report_date": datetime.now().strftime("%d.%m.%Y"),
        "total_expenses": round(sum(sorted_breakdown.values())),
        "breakdown": sorted_breakdown,
        "type": "by_category"
    }


@report()
def generate_weekly_report(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Отчет по дням недели.
    Группирует траты по дням недели (Пн, Вт, Ср...) и показывает общую сумму за каждый день.
    """
    days_map = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }
    weekday_totals = {day: 0.0 for day in days_map.values()}

    for t in transactions:
        try:
            tx_date = datetime.strptime(t["date"], "%Y-%m-%d")
            amount = float(t.get("amount", 0))
            if amount < 0:  # Только расходы
                day_name = days_map[tx_date.weekday()]
                weekday_totals[day_name] += abs(amount)
        except (ValueError, KeyError):
            continue

    # Округляем
    rounded_weekday = {day: round(total) for day, total in weekday_totals.items()}

    return {
        "report_date": datetime.now().strftime("%d.%m.%Y"),
        "total_expenses": round(sum(rounded_weekday.values())),
        "breakdown": rounded_weekday,
        "type": "by_weekday"
    }
