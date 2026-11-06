
"""
Константы и конфигурационные параметры проекта.
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Эндпоинты Московской Биржи (MOEX ISS API)
DOMAIN = "https://moex.com"
COUPON_PATH = "/iss/statistics/engines/stock/markets/bonds/bondization/"
BONDS_PATH = "/iss/engines/stock/markets/bonds/boards/TQOB/securities/"

# Файловая система
NAME_DB = "bonds_market.db"
PORTFOLIO_FILE = "portfolio.json"
 