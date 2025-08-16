import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd


def report_to_file(default_filename: Optional[str] = None):
    """Декоратор для сохранения результатов отчета в файл"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем результат выполнения функции
            result = func(*args, **kwargs)

            # Определяем имя файла
            filename = kwargs.get("report_filename", default_filename)
            if filename is None:
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{func.__name__}_{now}.json"

            try:
                if isinstance(result, pd.DataFrame):
                    result.to_json(filename, orient="records", indent=2)
                else:
                    with open(filename, "w") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                logging.info(f"Report saved to {filename}")
            except Exception as e:
                logging.error(f"Failed to save report: {e}")

            return result

        return wrapper

    return decorator


@report_to_file(default_filename="spending_by_category_report.json")
def spending_by_category(
    transactions_df: pd.DataFrame,
    category_name: str,
    target_date: Optional[str] = None,
    report_filename: Optional[str] = None,
) -> pd.DataFrame:
    """
    Анализирует расходы по категории за последние 3 месяца

    Args:
        transactions_df: DataFrame с транзакциями
        category_name: Название категории для анализа
        target_date: Дата отсчета (YYYY-MM-DD), None - текущая дата
        report_filename: Имя файла для сохранения отчета

    Returns:
        DataFrame с расходами по месяцам
    """
    try:
        # Определяем период анализа
        end_date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else datetime.now()
        start_date = end_date - timedelta(days=90)

        # Преобразуем даты в строки
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Фильтруем данные
        is_category = transactions_df["Категория"] == category_name
        in_date_range = (transactions_df["Дата операции"] >= start_date_str) & (
            transactions_df["Дата операции"] <= end_date_str
        )
        filtered_df = transactions_df[is_category & in_date_range].copy()

        # Добавляем месяц для группировки
        filtered_df["Месяц"] = pd.to_datetime(filtered_df["Дата операции"]).dt.to_period("M")

        # Группируем и агрегируем данные
        result = (
            filtered_df.groupby("Месяц").agg(Сумма=("Сумма платежа", "sum"), Кешбэк=("Кешбэк", "sum")).reset_index()
        )

        result["Месяц"] = result["Месяц"].astype(str)

        return result

    except Exception as e:
        logging.error(f"Error in spending analysis: {e}")
        raise
    # Пример использования
    # import pandas as pd
    # from src.reports import spending_by_category

    # Загрузка данных
    # transactions = pd.read_excel('operations.xlsx')

    # Вариант 1 - с текущей датой


# report_data = spending_by_category(transactions, "Супермаркеты")

# Вариант 2 - с указанной датой
# report_data = spending_by_category(
#     transactions,
#     "Рестораны",
#     date="2023-05-15"
# )

# Вариант 3 - с указанием имени файла
# report_data = spending_by_category(
#     transactions,
#     "Транспорт",
#     date="2023-05-15",
#     report_filename="transport_spending_report.json"
# )
