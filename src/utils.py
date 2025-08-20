import logging
from datetime import datetime


def validate_date(date_str: str) -> bool:
    """Проверяет корректность формата даты"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        logging.error(f"Invalid date format: {date_str}")
        return False


def load_user_settings() -> dict:
    """Загружает пользовательские настройки"""
    try:
        with open("user_settings.json") as f:
            import json

            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading user settings: {e}")
        return {}
