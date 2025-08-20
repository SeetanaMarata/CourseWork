import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import pandas as pd

from src.reports import spending_by_category
from src.services import calculate_cashback_categories
from src.utils import load_user_settings, validate_date
from src.views import main_page

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def convert_to_str_keys(data: List[Dict[Any, Any]]) -> List[Dict[str, Any]]:
    """Явно преобразует ключи словарей в строки"""
    return [{str(k): v for k, v in item.items()} for item in data]


class FinanceAnalyzer:
    def __init__(self, excel_path: str = "data/operations.xlsx"):
        self.excel_path = excel_path
        self.settings = load_user_settings()

        try:
            self.transactions_df = pd.read_excel(excel_path)
            self.transactions_df["Дата операции"] = pd.to_datetime(self.transactions_df["Дата операции"]).dt.strftime(
                "%Y-%m-%d"
            )
        except Exception as e:
            logging.error(f"Failed to load transactions data: {e}")
            raise

    def get_main_page_data(self, date_time: str) -> Dict[str, Any]:
        """Получает все данные для главной страницы"""
        if not validate_date(date_time):
            raise ValueError("Invalid date format. Expected YYYY-MM-DD HH:MM:SS")

        result = main_page(date_time, self.excel_path)

        # Явное преобразование типов для top_transactions
        if "top_transactions" in result:
            result["top_transactions"] = convert_to_str_keys(result["top_transactions"])
        return cast(Dict[str, Any], result)

    def analyze_cashback_categories(self, year: int, month: int) -> Dict[str, float]:
        """Анализирует выгодные категории для кешбэка"""
        transactions = convert_to_str_keys(self.transactions_df.to_dict("records"))
        return calculate_cashback_categories(transactions, year, month)

    def get_category_spending(self, category: str, target_date: Optional[str] = None) -> pd.DataFrame:
        """Получает траты по категории за последние 3 месяца"""
        return spending_by_category(self.transactions_df, category, target_date)

    @staticmethod
    def save_report(data: Any, report_type: str) -> str:
        """Сохраняет отчет в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/{report_type}_report_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                if isinstance(data, pd.DataFrame):
                    json_data = convert_to_str_keys(data.to_dict("records"))
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                elif isinstance(data, list):
                    json.dump(convert_to_str_keys(data), f, indent=2, ensure_ascii=False)
                else:
                    json.dump({str(k): v for k, v in data.items()}, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            logging.error(f"Failed to save report: {e}")
            raise


def run_analysis() -> None:
    """Основная функция для запуска анализа"""
    try:
        analyzer = FinanceAnalyzer()

        # 1. Получение данных для главной страницы
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_page_data = analyzer.get_main_page_data(current_datetime)

        # 2. Анализ выгодных категорий для кешбэка
        cashback_analysis = analyzer.analyze_cashback_categories(2023, 5)

        # 3. Получение трат по категории
        spending = analyzer.get_category_spending("Супермаркеты")

        # 4. Сохранение отчетов
        analyzer.save_report(main_page_data, "main_page")
        analyzer.save_report(cashback_analysis, "cashback_analysis")
        analyzer.save_report(spending.to_dict("records"), "category_spending")

    except Exception as e:
        logging.error(f"Application error: {e}")


if __name__ == "__main__":
    run_analysis()
    # Запустите модуль командой python -m src.main
