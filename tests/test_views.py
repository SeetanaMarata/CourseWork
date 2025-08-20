from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import get_card_stats, get_currency_rates, get_greeting, get_month_range


@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "Дата операции": ["2023-01-01", "2023-01-15", "2023-02-01"],
            "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654"],
            "Сумма платежа": [100.0, 200.0, 50.0],
            "Категория": ["Еда", "Транспорт", "Развлечения"],
            "Описание": ["Ресторан", "Такси", "Кино"],
        }
    )


@pytest.fixture
def sample_settings():
    return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}


def test_get_greeting():
    assert get_greeting("2023-01-01 08:00:00") == "Доброе утро"
    assert get_greeting("2023-01-01 13:00:00") == "Добрый день"
    assert get_greeting("2023-01-01 20:00:00") == "Добрый вечер"
    assert get_greeting("2023-01-01 02:00:00") == "Доброй ночи"


def test_get_card_stats(sample_transactions):
    stats = get_card_stats(sample_transactions, "2023-01-01", "2023-01-31")
    assert len(stats) == 1
    assert stats[0]["last_digits"] == "3456"
    assert stats[0]["total_spent"] == 300.0


@patch("requests.get")
def test_get_currency_rates(mock_get, sample_settings):
    mock_response = MagicMock()
    mock_response.json.return_value = {"rates": {"RUB": 75.0}}
    mock_get.return_value = mock_response

    rates = get_currency_rates(sample_settings["user_currencies"])
    assert len(rates) == 2
    assert rates[0]["currency"] in ["USD", "EUR"]


@pytest.mark.parametrize(
    "date_str,expected",
    [
        ("2023-01-15 12:00:00", ("2023-01-01", "2023-01-15")),
        ("2023-02-28 23:59:59", ("2023-02-01", "2023-02-28")),
    ],
)
def test_get_month_range(date_str, expected):
    assert get_month_range(date_str) == expected
