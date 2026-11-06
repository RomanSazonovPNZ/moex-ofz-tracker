"""Модуль для взаимодействия с API Московской Биржи (MOEX ISS)."""

from typing import Dict, Any
import requests
from constants import HEADERS, DOMAIN, BONDS_PATH, COUPON_PATH


def fetch_bond_raw_data(ticker: str) -> Dict[str, Any]:
    """Запрашивает базовые рыночные данные по ОФЗ."""
    url = f"{DOMAIN}{BONDS_PATH}{ticker}.json"
    response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    response.raise_for_status()
    return response.json()


def fetch_coupon_calendar_data(ticker: str) -> Dict[str, Any]:
    """Запрашивает исторический и будущий график купонов по ОФЗ."""
    url = f"{DOMAIN}{COUPON_PATH}{ticker}/couponstatements.json"
    response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    response.raise_for_status()
    return response.json()
