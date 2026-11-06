"""
Модуль для инициализации и синхронизации базы данных SQLite.
Не содержит логики вывода в консоль (UI-agnostic).
"""

import json
import logging
import os
import sqlite3
from typing import List, Tuple
from constants import NAME_DB, PORTFOLIO_FILE


# Отключаем предупреждения SSL, если это необходимо для специфичных сред (например, Android)
# При деплое на VPS рекомендуется удалить эту строку и настроить сертификаты
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настраиваем базовое логирование (в FastAPI оно настроится автоматически)
logger = logging.getLogger(__name__)


def create_tables() -> None:
    """Создает структуру таблиц в базе данных, если они отсутствуют."""
    with sqlite3.connect(NAME_DB) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS my_portfolio (
                ticker TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
        """)
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_value_clean REAL,
                total_value_dirty REAL,
                year_income_gross REAL,
                year_income_net REAL,
                monthly_forecast_json TEXT
            )
        """)


def sync_portfolio_from_json() -> bool:
    """
    Синхронизирует данные из JSON-файла в таблицу my_portfolio.
    Возвращает True в случае успеха, False если файл не найден.
    """
    if not os.path.exists(PORTFOLIO_FILE):
        logger.warning(f"Файл {PORTFOLIO_FILE} не найден.")
        return False

    with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
        portfolio_data = json.load(f)
    
    data_to_insert: List[Tuple[str, int]] = list(portfolio_data.items())
   
    with sqlite3.connect(NAME_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM my_portfolio")
        cursor.executemany("""
            INSERT OR REPLACE INTO my_portfolio (ticker, quantity) 
            VALUES (?, ?)
        """, data_to_insert)
        
    return True


def init_db() -> bool:
    """
    Полный цикл подготовки базы данных.
    Возвращает True, если портфель успешно синхронизирован.
    """
    create_tables()
    return sync_portfolio_from_json()

def get_portfolio_from_db(db_name: str) -> List[Tuple[str, int]]:
    """Извлекает список тикеров и их количество из базы данных."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, quantity FROM my_portfolio")
        return cursor.fetchall()



if __name__ == "__main__":
    # Если запускаем файл напрямую как скрипт, 
    # здесь (и только здесь!) мы можем использовать print для локальной отладки
    logging.basicConfig(level=logging.INFO)
    success = init_db()
    if success:
        print("База данных успешно инициализирована.")
    else:
        print("Ошибка при инициализации базы данных.")
