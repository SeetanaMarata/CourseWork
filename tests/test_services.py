import json

import pytest

from src.services import (calculate_cashback_categories,
                          get_cashback_categories_json)


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2023-01-15",
         "Категория": "Супермаркеты",
         "Сумма платежа": 5000, "Кешбэк": 50},
        {"Дата операции": "2023-01-20",
         "Категория": "Рестораны",
         "Сумма платежа": 3000, "Кешбэк": 150},
        {"Дата операции": "2023-02-01",
         "Категория": "Транспорт",
         "Сумма платежа": 2000},
    ]


def test_calculate_cashback_categories(sample_transactions):
    result = calculate_cashback_categories(sample_transactions, 2023, 1)
    assert "Супермаркеты" in result
    assert "Рестораны" in result
    assert "Транспорт" not in result
    assert result["Рестораны"] == 150
    assert result["Супермаркеты"] == 50


def test_calculate_cashback_with_default(sample_transactions):
    result = calculate_cashback_categories(sample_transactions, 2023, 2)
    assert "Транспорт" in result
    assert result["Транспорт"] == 20  # 1% от 2000


def test_get_cashback_categories_json(sample_transactions):
    json_result = get_cashback_categories_json(sample_transactions, 2023, 1)
    data = json.loads(json_result)
    assert isinstance(data, dict)
    assert len(data) == 2


@pytest.mark.parametrize("year,month,expected_count", [
    (2023, 1, 2),
    (2023, 2, 1),
    (2022, 1, 0)
])
def test_date_filtering(sample_transactions, year, month, expected_count):
    result = calculate_cashback_categories(sample_transactions, year, month)
    assert len(result) == expected_count


def test_invalid_date_format():
    transactions = [{"Дата операции": "invalid-date",
                     "Категория": "Тест", "Сумма платежа": 100}]
    result = calculate_cashback_categories(transactions, 2023, 1)
    assert len(result) == 0
