import json
import os

import pandas as pd
import pytest

from src.reports import datetime, report_to_file, spending_by_category, timedelta


@pytest.fixture
def sample_transactions_df():
    """Фикстура с тестовыми данными транзакций"""
    data = {
        "Дата операции": [
            (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=91)).strftime("%Y-%m-%d"),
            "2023-01-01",
        ],
        "Категория": ["Еда", "Еда", "Еда", "Транспорт"],
        "Сумма платежа": [1000, 2000, 3000, 500],
        "Кешбэк": [10, 20, 30, 5],
    }
    return pd.DataFrame(data)


def test_spending_by_category(sample_transactions_df):
    """Тест основной функциональности"""
    result = spending_by_category(sample_transactions_df, "Еда")
    assert len(result) == 2  # Должны быть только 2 транзакции
    # (3-я уже старше 3 месяцев)
    assert result["Сумма"].sum() == 3000


def test_spending_by_category_with_date(sample_transactions_df):
    """Тест с указанием конкретной даты"""
    test_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    result = spending_by_category(sample_transactions_df, "Еда", target_date=test_date)
    assert len(result) == 2  # Теперь корректно ожидаем 2 транзакции


def test_spending_by_category_no_data(sample_transactions_df):
    """Тест с несуществующей категорией"""
    result = spending_by_category(sample_transactions_df, "Несуществующая категория")
    assert len(result) == 0


def test_report_decorator(tmp_path, sample_transactions_df):
    """Тест декоратора с указанием имени файла"""
    os.chdir(tmp_path)

    @report_to_file("test_report.json")
    def test_func():
        return {"test": "data"}

    test_func()

    assert os.path.exists("test_report.json")
    with open("test_report.json") as f:
        data = json.load(f)
    assert data["test"] == "data"


def test_report_decorator_default_filename(tmp_path, sample_transactions_df):
    """Тест декоратора с автоматическим именем файла"""
    os.chdir(tmp_path)

    @report_to_file()
    def test_func():
        return {"test": "default"}

    test_func()

    files = [f for f in os.listdir() if f.startswith("report_test_func_")]
    assert len(files) == 1

    # Очистка временных файлов
    for f in files:
        os.remove(f)


def test_spending_columns(sample_transactions_df):
    """Тест структуры возвращаемых данных"""
    result = spending_by_category(sample_transactions_df, "Еда")
    expected_columns = ["Месяц", "Сумма", "Кешбэк"]
    assert all(col in result.columns for col in expected_columns)
