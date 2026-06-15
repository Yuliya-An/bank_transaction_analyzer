import pytest
import sys
from pathlib import Path
from src.services import analyze_cashback_categories, search_transactions, calculate_investment_savings

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_transactions():
    return [
        {"date": "2021-12-01", "amount": -1500.0, "category": "Супермаркеты", "description": "Пятерочка"},
        {"date": "2021-12-02", "amount": -500.0, "category": "Аптеки", "description": "Аптека"},
        {"date": "2021-12-03", "amount": 100000.0, "category": "Зарплата", "description": "Зарплата"},
        {"date": "2021-12-04", "amount": -300.0, "category": "Транспорт", "description": "Метро"},
        {"date": "2021-12-05", "amount": -1500.0, "category": "Супермаркеты", "description": "Ашан"},
        {"date": "2021-12-06", "amount": -200.0, "category": "Фастфуд", "description": "KFC"},
    ]


def test_analyze_cashback_categories(sample_transactions):
    """Тест расчета кэшбэка по категориям с указанием года и месяца."""
    result = analyze_cashback_categories(sample_transactions, 2021, 12)

    assert isinstance(result, dict)
    assert "Супермаркеты" in result
    assert result["Супермаркеты"] > 0
    assert "Зарплата" not in result


def test_search_transactions_by_phone(sample_transactions):
    """Тест поиска по номеру телефона (регулярные выражения)."""
    extended_data = sample_transactions + [
        {"date": "2021-12-07", "amount": -2500.0, "category": "Переводы",
         "description": "Перевод на карту +7 999 123-45-67"},
        {"date": "2021-12-08", "amount": -1000.0, "category": "Переводы",
         "description": "Перевод 8-800-555-35-35"},
    ]

    result = search_transactions(extended_data, "+7 999 123-45-67")
    assert len(result) > 0
    assert any("+7 999 123-45-67" in t["description"] for t in result)

    result = search_transactions(extended_data, "8-800-555-35-35")
    assert len(result) > 0
    assert any("8-800-555-35-35" in t["description"] for t in result)

    def test_search_transactions_by_transfer(sample_transactions):
        """Тест поиска переводов физическим лицам."""
        extended_data = sample_transactions + [
            {"date": "2021-12-09", "amount": -5000.0, "category": "Переводы",
             "description": "Перевод физическому лицу Иванов"},
            {"date": "2021-12-10", "amount": -3000.0, "category": "Переводы",
             "description": "Перевод на карту Петров"},
            {"date": "2021-12-11", "amount": -1500.0, "category": "Супермаркеты",
             "description": "Азбука вкуса"},
        ]

        result = search_transactions(extended_data, "физлицо")
        assert len(result) > 0
        assert any("Иванов" in t["description"] for t in result)

        result = search_transactions(extended_data, "перевод")
        assert len(result) >= 2

    def test_calculate_investment_savings(sample_transactions):
        """Комплексный тест инвесткопилки: разные лимиты и фильтрация доходов."""
        result_100 = calculate_investment_savings(sample_transactions, limit=100)
        assert isinstance(result_100, float)
        assert result_100 >= 0

        result_50 = calculate_investment_savings(sample_transactions, limit=50)
        assert isinstance(result_50, float)

        income_only = [
            {"date": "2021-12-01", "amount": 1000.0, "category": "Зарплата", "description": "Бонус"},
            {"date": "2021-12-02", "amount": 500.0, "category": "Кэшбэк", "description": "Возврат"},
        ]
        result_income = calculate_investment_savings(income_only, limit=100)
        assert result_income == 0.0
