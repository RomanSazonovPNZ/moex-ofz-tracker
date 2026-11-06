"""Модуль финансовых расчетов и аналитики портфеля."""

from datetime import datetime, date
from typing import Dict, List, Tuple, Any
import moex_client


def parse_bond_metrics(ticker: str, quantity: int) -> Dict[str, Any]:
    """Получает данные из API и рассчитывает показатели для конкретной ОФЗ."""
    raw_data = moex_client.fetch_bond_raw_data(ticker)

    sec_dict = dict(zip(raw_data["securities"]["columns"], raw_data["securities"]["data"][0]))
    market_dict = dict(zip(raw_data["marketdata"]["columns"], raw_data["marketdata"]["data"][0]))

    last_pct = market_dict.get("LAST")
    if last_pct is None or last_pct == 0 or float(last_pct) != float(last_pct):
        last_pct = market_dict.get("PREVPRICE", 0)

    face_value = float(sec_dict.get("FACEVALUE", 0))
    coupon_value = float(sec_dict.get("COUPONVALUE", 0))
    coupon_period = float(sec_dict.get("COUPONPERIOD", 0))
    nkd = float(sec_dict.get("ACCRUEDINT", 0))

    # Математика
    price_rub = round((float(last_pct) * face_value) / 100, 2)
    frequency = round(365 / coupon_period)
    year_coupon_rub = round(coupon_value * frequency, 2)

    current_yield = round((year_coupon_rub / price_rub) * 100, 2) if price_rub > 0 else 0.0
    yield_net = round(current_yield * 0.87, 2)

    return {
        "short_name": str(sec_dict.get("SHORTNAME")),
        "mat_date": str(sec_dict.get("MATDATE")),
        "face_value": face_value,
        "coupon_value": coupon_value,
        "coupon_period": coupon_period,
        "nkd": nkd,
        "next_coupon": str(sec_dict.get("NEXTCOUPON")),
        "last_pct": float(last_pct),
        "update_time": str(market_dict.get("UPDATETIME")),
        "price_rub": price_rub,
        "frequency": frequency,
        "current_yield": current_yield,
        "yield_net": yield_net,
        "position_value_clean": round(price_rub * quantity, 2),
        "position_nkd": round(nkd * quantity, 2),
        "position_year_coupon_gross": round(year_coupon_rub * quantity, 2),
        "position_year_coupon_net": round(year_coupon_rub * quantity * 0.87, 2),
    }


def calculate_monthly_coupons(ticker: str, quantity: int) -> Dict[str, float]:
    """Формирует календарь выплат по облигации на 12 месяцев вперед."""
    raw_data = moex_client.fetch_coupon_calendar_data(ticker)
    columns = raw_data["coupons"]["columns"]
    date_idx = columns.index("coupondate")
    value_idx = columns.index("value")
    
    bond_calendar: Dict[str, float] = {}
    today = date.today()
    try:
        one_year_later = today.replace(year=today.year + 1)
    except ValueError:
        one_year_later = today.replace(year=today.year + 1, day=today.day - 1)

    for row in raw_data["coupons"]["data"]:
        coupon_date = datetime.strptime(row[date_idx], "%Y-%m-%d").date()
        if today <= coupon_date <= one_year_later:
            month_key = coupon_date.strftime("%Y-%m")
            total_payout_gross = round(float(row[value_idx]) * quantity, 2)
            bond_calendar[month_key] = round(bond_calendar.get(month_key, 0.0) + total_payout_gross, 2)
            
    return bond_calendar


def aggregate_portfolio_analytics(portfolio: List[Tuple[str, int]]) -> Dict[str, Any]:
    """Собирает полную аналитику по всем бумагам в единый финансовый отчет."""
    bonds_analytics = {}
    monthly_calendar = {}
    total_value_clean = total_nkd = total_coupon_gross = total_coupon_net = 0.0

    for ticker, quantity in portfolio:
        try:
            bond_metrics = parse_bond_metrics(ticker, quantity)
            bonds_analytics[ticker] = {**bond_metrics, "quantity": quantity}

            total_value_clean += bond_metrics["position_value_clean"]
            total_nkd += bond_metrics["position_nkd"]
            total_coupon_gross += bond_metrics["position_year_coupon_gross"]
            total_coupon_net += bond_metrics["position_year_coupon_net"]

            # Календарь
            bond_calendar = calculate_monthly_coupons(ticker, quantity)
            for month, sum_gross in bond_calendar.items():
                if month not in monthly_calendar:
                    monthly_calendar[month] = {"gross": 0.0, "net": 0.0, "bonds": {}}
                
                monthly_calendar[month]["gross"] += sum_gross
                monthly_calendar[month]["net"] += round(sum_gross * 0.87, 2)
                monthly_calendar[month]["bonds"][ticker] = monthly_calendar[month]["bonds"].get(ticker, 0.0) + sum_gross
        except Exception:
            # В продакшене тут ошибку стоит залогировать через logger.exception
            continue

    return {
        "bonds": bonds_analytics,
        "calendar": dict(sorted(monthly_calendar.items())),
        "summary": {
            "total_value_clean": total_value_clean,
            "total_nkd": total_nkd,
            "total_value_dirty": total_value_clean + total_nkd,
            "total_coupon_gross": total_coupon_gross,
            "total_coupon_net": total_coupon_net,
            "total_yield_gross": round((total_coupon_gross / total_value_clean) * 100, 2) if total_value_clean > 0 else 0.0,
            "total_yield_net": round((total_coupon_net / total_value_clean) * 100, 2) if total_value_clean > 0 else 0.0,
        }
    }
