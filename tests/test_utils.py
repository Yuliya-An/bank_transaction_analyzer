import pytest
import json
import csv
from src.utils import (
    read_operations_from_json,
    read_operations_from_csv,
    read_data,
    get_events_page,
    search_transactions,
    calculate_investment_savings,
    analyze_cashback_categories,
    get_best_cashback_categories,
    get_analysis_page,
)


@pytest.fixture
def temp_json_file(tmp_path):
    data = [
        {"date": "2021-12-01", "amount": -1500.0, "category": "Супермаркеты", "description": "Пятерочка"},
        {"date": "2021-12-02", "amount": -500.0, "category": "Аптеки", "description": "Аптека"},
    ]
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path


@pytest.fixture
def temp_csv_file(tmp_path):
    data = [
        {"date": "2021-12-01", "amount": "-1500.0", "category": "Супермаркеты", "description": "Пятерочка"},
        {"date": "2021-12-02", "amount": "-500.0", "category": "Аптеки", "description": "Аптека"},
    ]
    file_path = tmp_path / "test.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "amount", "category", "description"], delimiter=";")
        writer.writeheader()
        writer.writerows(data)
    return file_path


def test_read_json(temp_json_file):
    res = read_operations_from_json(temp_json_file)
    assert len(res) == 2
    assert res[0]["category"] == "Супермаркеты"


def test_read_csv(temp_csv_file):
    res = read_operations_from_csv(temp_csv_file)
    assert len(res) == 2
    assert res[1]["description"] == "Аптека"


def test_read_data_xlsx_success(tmp_path):
    # Создаем минимальный xlsx через pandas для проверки
    import pandas as pd
    file_path = tmp_path / "operations.xlsx"
    df = pd.DataFrame([{"date": "2021-12-01", "amount": -100, "category": "Тест", "description": "Оплата"}])
    df.to_excel(file_path, index=False)

    res = read_data(file_path)
    assert len(res) == 1
    assert res[0]["category"] == "Тест"


def test_read_data_fallback():
    # Проверяем, что при отсутствии файла возвращается пустой список (без ошибок!)
    res = read_data("non_existent_file.xlsx")
    assert isinstance(res, list)
    assert len(res) == 0

    def test_search_transactions():
        data = [
            {"description": "Покупка в Пятерочке", "category": "Супермаркеты", "amount": -100},
            {"description": "Перевод от мамы", "category": "Переводы", "amount": 500},
            {"description": "Аптека Ригла", "category": "Аптеки", "amount": -200},
        ]
        # Поиск по описанию
        res1 = search_transactions(data, "Пятерочка")
        assert len(res1) == 1
        assert res1[0]["description"] == "Покупка в Пятерочке"

        # Поиск по категории
        res2 = search_transactions(data, "Аптеки")
        assert len(res2) == 1
        assert res2[0]["category"] == "Аптеки"

    def test_search_transactions_empty():
        data = [{"description": "Кофе", "category": "Кафе", "amount": -200}]
        res = search_transactions(data, "Спецслужбы")
        assert len(res) == 0

    def test_calculate_investment_savings():
        # Пример: -123 (остаток 7), -456 (остаток 4), 100 (доход - игнорируем)
        # Должно накопиться: (10-3) + (10-6) = 7 + 4 = 11.0
        data = [
            {"amount": -123},
            {"amount": -456},
            {"amount": 100},
        ]
        res = calculate_investment_savings(data)
        assert res == 11.0

    def test_calculate_investment_savings_with_limit():
        # Проверяем, что функция принимает аргумент limit без ошибок
        data = [{"amount": -123}]
        res = calculate_investment_savings(data, limit=50)
        assert res == 7.0


def test_analyze_cashback_categories():
    data = [
        {"date": "2021-12-01", "amount": -1000, "category": "Супермаркеты"},
        {"date": "2021-12-02", "amount": -200, "category": "Аптеки"},
        {"date": "2021-12-03", "amount": -500, "category": "Супермаркеты"},
    ]
    res = analyze_cashback_categories(data, 2021, 12)
    assert isinstance(res, dict)
    assert "total_cashback" in res
    # Супермаркеты: 1500 * 0.05 = 75; Аптеки: 200 * 0.1 = 20; Итого: 95.0
    assert res["total_cashback"] == 95.0


def test_get_best_cashback_categories():
    data = [
        {"date": "2021-12-01", "amount": -1000, "category": "Супермаркеты"},
        {"date": "2021-12-02", "amount": -200, "category": "Аптеки"},
        {"date": "2021-12-03", "amount": -500, "category": "Супермаркеты"},
    ]
    res = get_best_cashback_categories(data, 2021, 12)
    assert isinstance(res, list)
    assert len(res) == 2
    # Супермаркеты: 75.0, Аптеки: 20.0
    assert res[0][0] == "Супермаркеты"
    assert res[0][1] == 75.0


def test_get_events_page():
    data = [
        {"date": "2021-12-01", "amount": -1000, "category": "Супермаркеты", "description": "Лента"},
        {"date": "2021-12-15", "amount": -500, "category": "Аптеки", "description": "Аптека"},
        {"date": "2021-12-20", "amount": 2000, "category": "Зарплата", "description": "Зарплата"},
    ]
    res = get_events_page(data, "ALL")
    assert isinstance(res, dict)
    assert res["income"] == 2000.0
    assert res["expense"] == 1500.0
    assert res["balance"] == 500.0


def test_get_analysis_page():
    data = [
        {"date": "2021-12-01", "amount": -123, "category": "Супермаркеты", "description": "Магнит"},
        {"date": "2021-12-02", "amount": -456, "category": "Аптеки", "description": "Аптека"},
    ]
    res = get_analysis_page(data, query="Магнит", year=2021, month=12)
    assert isinstance(res, dict)
    assert "search" in res
    assert "savings" in res
    assert "best_cats" in res
    assert "cashback_report" in res
