"""
Модуль для парсинга и расчета календаря купонных выплат ОФЗ.
"""

from datetime import datetime, date
from typing import Dict
import requests
from constants import HEADERS, DOMAIN, COUPON_PATH


def get_monthly_coupons(ticker: str, quantity: int) -> Dict[str, float]:
    """
    Запрашивает график купонов для ОФЗ и формирует прогноз выплат 
    на 12 месяцев вперед от текущей даты.
    """
    url = f"{DOMAIN}{COUPON_PATH}{ticker}/couponstatements.json"
    
    response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    response.raise_for_status()
    data = response.json()
    
    # Извлекаем индексы колонок из метаданных ответа MOEX
    columns = data["coupons"]["columns"]
    date_idx = columns.index("coupondate")
    value_idx = columns.index("value")
    
    bond_calendar: Dict[str, float] = {}
    
    today = date.today()
    # Считаем дату окончания периода (через год) с учетом високосных годов
    try:
        one_year_later = today.replace(year=today.year + 1)
    except ValueError:
        # Хэндл для 29 февраля
        one_year_later = today.replace(year=today.year + 1, day=today.day - 1)

    for row in data["coupons"]["data"]:
        # Строку даты "YYYY-MM-DD" превращаем в объект date
        coupon_date = datetime.strptime(row[date_idx], "%Y-%m-%d").date()
        
        # Фильтруем: выплата должна быть в диапазоне [сегодня; через год]
        if today <= coupon_date <= one_year_later:
            month_key = coupon_date.strftime("%Y-%m")
            coupon_rub = float(row[value_idx])
            
            total_payout_gross = round(coupon_rub * quantity, 2)
            
            # Аккумулируем сумму за месяц
            bond_calendar[month_key] = round(bond_calendar.get(month_key, 0.0) + total_payout_gross, 2)
            
    return bond_calendar
