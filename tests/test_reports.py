import pytest
import sys
import json
from pathlib import Path
from datetime import datetime
from src.reports import report
from src.reports import generate_spending_report, generate_weekly_report
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_reports_dir(tmp_path):
    """Создаем временную папку для отчетов."""
    test_dir = tmp_path / "reports"
    test_dir.mkdir(exist_ok=True)
    return str(test_dir)


def test_report_decorator_creates_file(temp_reports_dir):
    """Тест: декоратор создает JSON-файл."""

    @report(temp_reports_dir)
    def test_func():
        return {"status": "ok", "balance": 1000}

    test_func()

    files = list(Path(temp_reports_dir).glob("*.json"))
    assert len(files) > 0


def test_report_decorator_filename_has_date(temp_reports_dir):
    """Тест: имя файла содержит дату."""

    @report(temp_reports_dir)
    def another_func():
        return {"message": "hello"}

    another_func()

    files = list(Path(temp_reports_dir).glob("*.json"))
    assert len(files) > 0

    today_str = datetime.now().strftime("%Y%m%d")
    assert any(today_str in f.name for f in files)


def test_report_decorator_with_list_return(temp_reports_dir):
    """Тест: декоратор работает с возвратом списка."""

    @report(temp_reports_dir)
    def list_func():
        return [{"id": 1}, {"id": 2}]

    list_func()

    files = list(Path(temp_reports_dir).glob("*.json"))
    assert len(files) > 0

    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 2


@pytest.fixture
def sample_transactions():
    """Набор тестовых транзакций для проверки отчетов."""
    return [
        {"date": "2024-01-05", "category": "Супермаркеты", "amount": -1500.50},
        {"date": "2024-01-06", "category": "Аптеки", "amount": -800.75},
        {"date": "2024-01-06", "category": "Кафе", "amount": -1200.00},
        {"date": "2024-01-07", "category": "Супермаркеты", "amount": -2300.00},
        {"date": "2024-01-07", "category": "Транспорт", "amount": -500.60},
        {"date": "2024-01-08", "category": "Зарплата", "amount": 50000.00},  # Доход, не должен попасть в отчет
        {"date": "2024-01-08", "category": "Аптеки", "amount": -300.00},
        {"date": "2024-01-09", "category": "Кафе", "amount": -450.25},
    ]


def test_spending_report_only_expenses(sample_transactions):
    """Тест: в отчет попадают только расходы (отрицательные суммы)."""
    result = generate_spending_report(sample_transactions)

    # Зарплата (50000) не должна быть в отчете
    assert "Зарплата" not in result["breakdown"]
    assert all(amount >= 0 for amount in result["breakdown"].values())


def test_spending_report_sorted(sample_transactions):
    """Тест: категории отсортированы по убыванию суммы."""
    result = generate_spending_report(sample_transactions)

    amounts = list(result["breakdown"].values())
    assert amounts == sorted(amounts, reverse=True)


def test_spending_report_rounded(sample_transactions):
    """Тест: все суммы округлены до целых чисел."""
    result = generate_spending_report(sample_transactions)

    for amount in result["breakdown"].values():
        assert isinstance(amount, int) or (isinstance(amount, float) and amount == int(amount))


def test_weekly_report_not_monday(sample_transactions):
    """Тест: проверяем, что 2024-01-05 — это пятница (индекс 4)."""
    from datetime import datetime
    friday = datetime(2024, 1, 5)
    assert friday.weekday() == 4  # Пятница


def test_weekly_report_structure(sample_transactions):
    """Тест: структура отчета по дням недели корректна."""
    result = generate_weekly_report(sample_transactions)

    # Проверяем, что в отчете 7 дней недели
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for day in days:
        assert day in result["breakdown"]

    # Проверяем, что total_expenses совпадает с суммой всех дней
    assert result["total_expenses"] == sum(result["breakdown"].values())


def test_weekly_report_only_expenses(sample_transactions):
    """Тест: доход (Зарплата) не влияет на отчет по дням недели."""
    result = generate_weekly_report(sample_transactions)

    # Понедельник (2024-01-08) — должен быть 0, так как зарплата не считается
    assert result["breakdown"]["Понедельник"] == 300
