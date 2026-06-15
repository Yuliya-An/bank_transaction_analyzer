import pytest
from src.views import get_main_page, get_events_page, get_analysis_page


@pytest.fixture
def mock_data():
    return [
        {"date": "2021-12-01", "amount": -1500, "category": "Супермаркеты", "description": "Продукты"},
        {"date": "2021-12-03", "amount": -500, "category": "Аптеки", "description": "Лекарства"},
        {"date": "2021-12-05", "amount": 100000, "category": "Зарплата", "description": "Оклад"},
        {"date": "2021-12-10", "amount": -200, "category": "Кафе", "description": "Кофе"},
    ]


@pytest.fixture
def mock_settings():
    return {
        "user_name": "Пользователь",
        "cards": ["4444"],
        "currency": "RUB",
        "currencies": ["USD", "EUR"],
        "stocks": ["AAPL", "TSLA"],
    }


def test_get_main_page_recent_activity_and_balance(mock_data, mock_settings):
    result = get_main_page(mock_data, mock_settings)

    assert isinstance(result, dict)
    assert "greeting" in result
    assert "Пользователь" in result["greeting"]
    assert result["cards"] == ["4444"]

    # Проверка сортировки: самая свежая дата (2021-12-10) должна быть первой
    assert result["recent_activity"][0]["date"] == "2021-12-10"
    assert len(result["recent_activity"]) <= 5

    # Баланс: 100000 - 1500 - 500 - 200 = 97800.0
    assert result["balance"] == 97800.0
    assert "currency_rates" in result
    assert "stock_prices" in result


def test_get_events_page_all(mock_data):
    result = get_events_page(mock_data, period="ALL")

    assert isinstance(result, dict)
    assert result["period"] == "ALL"
    assert result["total_sum"] == 97800.0
    assert result["count"] == 4
    assert "Супермаркеты" in result["breakdown"]
    assert "Зарплата" in result["breakdown"]


def test_get_analysis_page_with_year_month(mock_data):
    result = get_analysis_page(mock_data, year=2021, month=12)

    assert isinstance(result, dict)
    assert "best_categories" in result
    assert "cashback_report" in result
    assert "investment_savings" in result
    assert isinstance(result["best_categories"], list)
    assert isinstance(result["cashback_report"], dict)


def test_get_analysis_page_search(mock_data):
    result = get_analysis_page(mock_data, query="Продукты")

    assert isinstance(result, dict)
    assert "search_results" in result
    search_res = result["search_results"]
    assert isinstance(search_res, list)
    assert len(search_res) == 1
    assert search_res[0]["description"] == "Продукты"
    assert "investment_savings" in result
