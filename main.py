"""Точка входа CLI-приложения для мониторинга портфеля ОФЗ."""

import logging
from constants import NAME_DB
import database
import services

logging.basicConfig(level=logging.INFO)


def show_terminal_report(report: dict) -> None:
    """Выводит полную аналитику в консоль со всеми деталями по каждой ОФЗ."""
    print("\n" + "="*60)
    print("🚀 НАЧАЛО СБОРА И ВЫВОДА ДАННЫХ ПО ОФЗ (Данные MOEX ISS)")
    print("="*60)
    
    for ticker, data in report["bonds"].items():
        print(f"\n📌 ОФЗ: {ticker} ({data['short_name']})")
        print(f"   📅 Дата погашения:   {data['mat_date']}")
        print(f"   💰 Номинал:          {data['face_value']:.1f} руб.")
        print(f"   📅 Следующий купон:   {data['next_coupon']}")
        print(f"   📈 Текущая цена:     {data['price_rub']} руб. ({data['last_pct']}%)")
        print(f"   💸 Текущий НКД:      {data['nkd']} руб.")
        print(f"   💵 Размер купона:    {data['coupon_value']} руб. (каждые {int(data['coupon_period'])} дн.)")
        print(f"   📅 Выплат в год:     {data['frequency']}")
        print(f"   📊 Доходность купонная (гряз): {data['current_yield']}%")
        print(f"   🔥 Доходность купонная (чист): {data['yield_net']}%")
        print(f"   🕒 Время обновления: {data['update_time']}")
        print(f"   📦 Всего в портфеле: {data['quantity']} шт.")
        print("-" * 45)
        print(f"   💵 Годовой купонный доход позиции (без НДФЛ):  {data['position_year_coupon_gross']:_.2f} руб.")
        print(f"   💵 Годовой купонный доход позиции (чистый, 13%): {data['position_year_coupon_net']:_.2f} руб.")
        print("-" * 55)

    print("\n📅 ПРОГНОЗ КУПОННЫХ ВЫПЛАТ ПО МЕСЯЦАМ (На 12 месяцев):")
    for month, values in report["calendar"].items():
        print(f"\n   📅 Месяц: {month} -> ")
        print(f"         Общая сумма (грязными): {values['gross']:_.2f} руб.")
        print(f"         Чистыми (НДФЛ -13%): {values['net']:_.2f} руб.")
        print("      Детализация по ОФЗ:")
        for bond_ticker, bond_gross in values["bonds"].items():
            bond_net = round(bond_gross * 0.87, 2)
            print(f"        🔹 {bond_ticker}: {bond_gross:_.2f} руб. (чистыми: {bond_net:_.2f} руб.)")

    sm = report["summary"]
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ СВОДКА ПО ПОРТФЕЛЮ:")
    print("="*60)
    print(f"   💵 Чистая стоимость (без НКД):    {sm['total_value_clean']:_.2f} руб.")
    print(f"   📦 Накопленный купон (общий НКД): {sm['total_nkd']:_.2f} руб.")
    print(f"   💰 Полная стоимость (с НКД):      {sm['total_value_dirty']:_.2f} руб.")
    print(f"   🔥 ВСЕГО ГОДОВОЙ КУПОННЫЙ ДОХОД\n                   (без уплаты НДФЛ): {sm['total_coupon_gross']:_.2f} руб. ({sm['total_yield_gross']}%)")
    print(f"   🍀 ВСЕГО ГОДОВОЙ КУПОННЫЙ ДОХОД\n                (чистый, - НДФЛ 13%): {sm['total_coupon_net']:_.2f} руб. ({sm['total_yield_net']}%)")
    print("="*60 + "\n")


def main():
    # Шаг 1: Инициализация хранилища
    if database.init_db():
        print("✅ База данных готова к работе.")
    
    # Шаг 2: Получение состава портфеля
    portfolio = database.get_portfolio_from_db(NAME_DB)
    if not portfolio:
        print("❌ Портфель пуст. Заполните portfolio.json!")
        return

    # Шаг 3: Расчет аналитики
    print("⏳ Запрашиваем данные с Мосбиржи...")
    report = services.aggregate_portfolio_analytics(portfolio)
    
    # Шаг 4: Вывод результатов
    show_terminal_report(report)


if __name__ == "__main__":
    main()
