import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Hashable, List

import pandas as pd
import requests


def get_greeting(time_str: str) -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").time()
    if 5 <= time.hour < 12:
        return "Доброе утро"
    elif 12 <= time.hour < 18:
        return "Добрый день"
    elif 18 <= time.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_stats(df: pd.DataFrame, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Возвращает статистику по картам"""
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    period_df = df[mask]

    cards = []
    for card in period_df["Номер карты"].unique():
        card_df = period_df[period_df["Номер карты"] == card]
        total_spent = card_df["Сумма платежа"].sum()
        cashback = total_spent / 100
        cards.append({"last_digits": card[-4:], "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)})
    return cards


def get_top_transactions(df: pd.DataFrame, start_date: str, end_date: str, n: int = 5) -> list[dict[Hashable, Any]]:
    """Возвращает топ-N транзакций по сумме платежа"""
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    period_df = df[mask]

    top_transactions = period_df.nlargest(n, "Сумма платежа")
    return (
        top_transactions[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
        .rename(
            columns={
                "Дата операции": "date",
                "Сумма платежа": "amount",
                "Категория": "category",
                "Описание": "description",
            }
        )
        .to_dict("records")
    )


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют через API"""
    rates = []
    for currency in currencies:
        try:
            response = requests.get(f"https://api.exchangerate-api." f"com/v4/latest/{currency}")
            data = response.json()
            rates.append({"currency": currency, "rate": data["rates"]["RUB"]})
        except Exception as e:
            logging.error(f"Error fetching currency rates: {e}")
    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    prices = []
    for stock in stocks:
        try:
            url = (
                f"https://www.alphavantage."
                f"co/query?function=GLOBAL_QUOTE&symbol="
                f"{stock}&apikey={os.getenv('ALPHAVANTAGE_API_KEY')}"
            )
            response = requests.get(url)
            data = response.json()
            price = float(data["Global Quote"]["05. price"])
            # Если "05. price" — строка, проблем нет
            prices.append({"stock": stock, "price": price})
            # str  # float (Any)
        except Exception as e:
            logging.error(f"Error fetching {stock} price: {e}")
    return prices


def get_month_range(date_str: str) -> tuple:
    """Возвращает начало и конец месяца для заданной даты"""
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = date.replace(day=1).strftime("%Y-%m-%d")
    end_date = date.strftime("%Y-%m-%d")
    return start_date, end_date


def main_page(date_time: str, excel_path: str = "data/operations.xlsx") -> Dict[str, Any]:
    """Главная функция для генерации JSON-ответа"""
    try:
        # Загрузка данных
        df = pd.read_excel(excel_path)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"]).dt.strftime("%Y-%m-%d")

        # Загрузка настроек пользователя
        with open("user_settings.json") as f:
            settings = json.load(f)

        # Получение данных
        start_date, end_date = get_month_range(date_time)

        return {
            "greeting": get_greeting(date_time),
            "cards": get_card_stats(df, start_date, end_date),
            "top_transactions": get_top_transactions(df, start_date, end_date),
            "currency_rates": get_currency_rates(settings["user_currencies"]),
            "stock_prices": get_stock_prices(settings["user_stocks"]),
        }
    except Exception as e:
        logging.error(f"Error in main_page: {e}")
        raise
