import json
from pathlib import Path
from src.utils import (read_data, get_main_page, get_events_page, get_analysis_page)


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "user_settings.json"


def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    user_settings = load_settings()
    data = read_data(DATA_DIR)

    print("=== Система анализа банковских транзакций ===")
    print("1: Главная страница")
    print("2: События (ALL)")
    print("3: Поиск транзакций")
    print("4: Анализ кэшбэка")
    print("0: Выход")

    choice = input("Выбери опцию: ")

    if choice == "1":
        result = get_main_page(data, user_settings)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif choice == "2":
        period = input("Введи период (W/M/Y/ALL): ").upper()
        result = get_events_page(data, period)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif choice == "3":
        query = input("Введите строку для поиска: ")
        result = get_analysis_page(data, query=query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif choice == "4":
        year = int(input("Год (например 2023): "))
        month = int(input("Месяц (1-12): "))
        result = get_analysis_page(data, year=year, month=month)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif choice == "0":
        print("Выход. Удачного дня!")
    else:
        print("Неверный выбор. Попробуй снова.")


if __name__ == "__main__":
    main()
