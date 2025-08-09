import json
import logging
from datetime import datetime
from typing import Any, Dict, List


def calculate_cashback_categories(transactions: List[Dict[str, Any]],
                                  year: int,
                                  month: int) -> Dict[str, float]:
    """
    Анализирует выгодность категорий для повышенного
    кешбэка за указанный месяц и год.

    Args:
        transactions: Список транзакций в формате словарей
        year: Год для анализа
        month: Месяц для анализа (1-12)

    Returns:
        Словарь с категориями и суммарным кешбэком по ним
    """
    try:
        # Фильтрация транзакций по дате
        filtered_transactions = filter(
            lambda t: _is_transaction_in_period(
                t, year, month), transactions)

        # Группировка по категориям и расчет кешбэка
        category_cashback = {}
        for transaction in filtered_transactions:
            category = transaction.get("Категория", "Другое")
            amount = transaction.get("Сумма платежа", 0)
            cashback = transaction.get("Кешбэк", 0)

            if category not in category_cashback:
                category_cashback[category] = 0.0

            category_cashback[category] += cashback \
                if cashback else amount * 0.01
            # 1% если кешбэк не указан

        # Сортировка по убыванию кешбэка
        sorted_categories = sorted(category_cashback.items(),
                                   key=lambda item: item[1], reverse=True)

        return dict(sorted_categories)

    except Exception as e:
        logging.error(f"Error in calculate_cashback_categories: {e}")
        raise


def _is_transaction_in_period(transaction: dict[str, Any],
                              year: int,
                              month: int) -> bool:
    """Проверяет, относится ли транзакция к указанному периоду"""
    date_str = transaction.get("Дата операции")
    if not date_str:
        return False

    try:
        transaction_date = datetime.strptime(date_str, "%Y-%m-%d")
        return (transaction_date.year == year and transaction_date
                .month == month)
    except ValueError:
        logging.warning(f"Invalid date format in transaction: {date_str}")
        return False


def get_cashback_categories_json(data: List[Dict[str, Any]],
                                 year: int, month: int) -> str:
    """
    Возвращает JSON с анализом выгодных категорий для кешбэка

    Args:
        data: Список транзакций
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        JSON-строка с результатами анализа
    """
    result = calculate_cashback_categories(data, year, month)
    return json.dumps(result, ensure_ascii=False, indent=2)


# Пример использования
# from src.services import get_cashback_categories_json

# transactions = [{'Дата операции': '2023-05-10',
# 'Категория': 'Супермаркеты', 'Сумма платежа': 10000},
#    {'Дата операции': '2023-05-15', 'Категория': 'Рестораны',
#    'Сумма платежа': 5000, 'Кешбэк': 250}]

# result_json = get_cashback_categories_json(transactions, 2023, 5)
# print(result_json)
