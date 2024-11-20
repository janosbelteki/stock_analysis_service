import logging
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta

from app.data_collector import fetch_stock_data, save_to_db
from app.db_config import DB_PATH
from app.db_utils import get_db_connection


def analyze_stock_data(symbol):
    """
    Fetch data from the database and perform analysis for the specified stock symbol.
    """
    data = get_stock_data_from_db_for_last_thirty_days(symbol)
    return perform_comprehensive_analysis(symbol, data)


def get_stock_data_from_db_for_last_thirty_days(symbol):
    thirty_days_ago_str = check_date_and_update_database_if_needed(symbol)
    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, open_price, close_price, high_price, low_price, volume
            FROM stock_prices
            WHERE symbol = ? AND date >= ?
            ORDER BY date
        """,
            (symbol, thirty_days_ago_str),
        )
        rows = cursor.fetchall()
        return [
            {
                "date": row[0],
                "open": row[1],
                "close": row[2],
                "high": row[3],
                "low": row[4],
                "volume": row[5],
            }
            for row in rows
        ]


def check_date_and_update_database_if_needed(symbol):
    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM stock_prices WHERE symbol = ?", (symbol,))
        latest_date_str = cursor.fetchone()[0]
        try:
            start_date = (
                datetime.strptime(latest_date_str, "%Y-%m-%d").date()
                if latest_date_str
                else None
            )
        except ValueError as e:
            logging.error(
                f"Invalid date format in database: {latest_date_str}. Error: {e}"
            )
            start_date = None
        end_date = get_last_trading_day(datetime.now(pytz.timezone("America/New_York")))

        if start_date is None or start_date < end_date.date():
            logging.info(
                f"Fetching data for {symbol} from {start_date} to {end_date.date()}"
            )
            data = fetch_stock_data(
                symbol,
                start_date=start_date + timedelta(days=1) if start_date else None,
                end_date=end_date,
            )
            if data:
                save_to_db(symbol, data)
            else:
                logging.warning(f"No data found for {symbol} in the given range.")

        thirty_days_ago = end_date - timedelta(days=30)
        return thirty_days_ago.strftime("%Y-%m-%d")


def get_last_trading_day(date: datetime.date) -> datetime.date:
    """
    Returns the last trading day before the given date.
    If the date is a weekday, returns the previous day.
    If the date is a weekend, returns the previous Friday.
    """
    if date.weekday() in {5, 6}:
        return date - relativedelta(weekday=4)
    return date - timedelta(days=1)


def perform_comprehensive_analysis(symbol, data):
    """
    Perform detailed analysis for all price types, volume, and additional metrics.
    """
    close_prices = [entry["close"] for entry in data]
    open_prices = [entry["open"] for entry in data]
    high_prices = [entry["high"] for entry in data]
    low_prices = [entry["low"] for entry in data]
    volumes = [entry["volume"] for entry in data]
    dates = [entry["date"] for entry in data]

    close_analysis = perform_default_price_analysis(close_prices, dates)
    open_analysis = perform_default_price_analysis(open_prices, dates)
    high_analysis = perform_default_price_analysis(high_prices, dates)
    low_analysis = perform_default_price_analysis(low_prices, dates)
    volume_analysis = perform_volume_analysis(volumes, dates)

    add_total_return_to_analysis(close_analysis, close_prices, dates)
    add_risk_reward_ratio_to_analysis(close_analysis)
    correlation_dict_key_str = "_correlation_coeff"
    add_top_stock_correlation_to_analysis(
        symbol, close_analysis, close_prices, correlation_dict_key_str
    )

    combined_analysis = {
        "close": close_analysis,
        "open": open_analysis,
        "high": high_analysis,
        "low": low_analysis,
        "volume": volume_analysis,
    }
    save_analysis_results_to_db(symbol, combined_analysis, correlation_dict_key_str)
    return combined_analysis


def perform_default_price_analysis(prices, dates):
    """
    Perform trend and volatility analysis for a specific price type.
    """
    return {
        "trend": {
            7: do_analysis_method_over_period("trend", prices, dates, 5),
            30: do_analysis_method_over_period("trend", prices, dates, 30),
        },
        "volatility": {
            7: do_analysis_method_over_period("volatility", prices, dates, 5),
            30: do_analysis_method_over_period("volatility", prices, dates, 30),
        },
        "avg_daily_return": {
            7: do_analysis_method_over_period("avg_daily_return", prices, dates, 5),
            30: do_analysis_method_over_period("avg_daily_return", prices, dates, 30),
        },
    }


def do_analysis_method_over_period(feature, prices, dates, period):
    """
    Perform the specified analysis method for a given period.
    Uses only data points within the specified date range.
    """
    filtered_prices = filter_data_for_period(prices, dates, period)

    analysis_methods = {
        "trend": calculate_price_trend_over_period,
        "volatility": calculate_volatility_over_period,
        "avg_daily_return": calculate_avg_daily_return_over_period,
        "total_return": calculate_total_return_over_period,
    }
    func = analysis_methods.get(feature)
    if func:
        return func(filtered_prices)
    else:
        raise ValueError(f"Invalid analysis method: {feature}")


def filter_data_for_period(data_to_filter, dates, period):
    if len(dates) < 2:
        return None

    period_start_date = dates[-1] - timedelta(days=period + 1)
    filtered_indices = [i for i, date in enumerate(dates) if date >= period_start_date]

    if len(filtered_indices) < 2:
        return None

    filtered_data = [data_to_filter[i] for i in filtered_indices]
    return filtered_data


def calculate_price_trend_over_period(filtered_prices):
    filtered_days = np.arange(len(filtered_prices))
    return np.polyfit(filtered_days[1:], filtered_prices[1:], 1)[0]


def calculate_volatility_over_period(filtered_prices):
    return np.std(np.diff(filtered_prices[-1 * len(filtered_prices) :]))


def calculate_avg_daily_return_over_period(filtered_prices):
    return np.mean(
        np.diff(filtered_prices[-1 * len(filtered_prices) - 1 :])
        / filtered_prices[-1 * len(filtered_prices) - 1 - 1 : -1]
    )


def calculate_total_return_over_period(filtered_prices):
    return (
        (filtered_prices[-1] - filtered_prices[0]) / filtered_prices[0]
    ) * 100  # Not taking potential dividends into account


def perform_volume_analysis(volumes, dates):
    filtered_volumes = filter_data_for_period(volumes, dates, 30)
    return {
        "avg": {
            7: np.mean(filtered_volumes[-5:]),
            30: np.mean(filtered_volumes[-30:]),
        },
        "volatility": {
            7: np.std(filtered_volumes[-5:]),
            30: np.std(filtered_volumes[-30:]),
        },
    }


def add_total_return_to_analysis(analysis, prices, dates):
    analysis["total_return"] = {
        7: do_analysis_method_over_period("total_return", prices, dates, 5),
        30: do_analysis_method_over_period("total_return", prices, dates, 30),
    }


def add_risk_reward_ratio_to_analysis(analysis):
    analysis["risk_reward_ratio"] = {
        7: analysis["avg_daily_return"][7] / analysis["volatility"][7],
        30: analysis["avg_daily_return"][30] / analysis["volatility"][30],
    }


def add_top_stock_correlation_to_analysis(
    symbol, analysis, prices, correlation_dict_key_str
):
    top_stock, top_stock_close_prices_over_period = (
        get_top_stock_by_dollar_volume_over_period(symbol, 5)
    )
    if top_stock != symbol:
        key = str(top_stock) + correlation_dict_key_str
        if key not in analysis:
            analysis[key] = {}
        analysis[key][7] = calculate_correlation_coefficient_for_top_stock_over_period(
            prices, top_stock_close_prices_over_period
        )
    else:
        logging.info(
            f"Top performing stock by dollar volume in the past week was {symbol} itself!"
        )

    top_stock, top_stock_close_prices_over_period = (
        get_top_stock_by_dollar_volume_over_period(symbol, 30)
    )
    if top_stock != symbol:
        key = str(top_stock) + correlation_dict_key_str
        if key not in analysis:
            analysis[key] = {}
        analysis[key][30] = calculate_correlation_coefficient_for_top_stock_over_period(
            prices, top_stock_close_prices_over_period
        )
    else:
        logging.info(
            f"Top performing stock by dollar volume in the past month was {symbol} itself!"
        )


def get_top_stock_by_dollar_volume_over_period(symbol, period):
    with get_db_connection(DB_PATH) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT DISTINCT symbol
                    FROM stock_prices
                    WHERE symbol != ?
                """,
                (symbol,),
            )
            symbols = [row[0] for row in cursor.fetchall()]

            highest_dollar_volume = 0
            top_stock = None

            for symbol in symbols:
                cursor.execute(
                    """
                    SELECT close_price, volume
                    FROM stock_prices
                    WHERE symbol = ?
                    ORDER BY date DESC LIMIT ?
                """,
                    (symbol, period),
                )

                rows = cursor.fetchall()
                if rows:
                    dollar_volume = sum(
                        price * volume for price, volume in rows if price and volume
                    )

                    if dollar_volume > highest_dollar_volume:
                        highest_dollar_volume = dollar_volume
                        top_stock = symbol
            top_stock_close_prices_over_period = [row[0] for row in rows]
            return top_stock, top_stock_close_prices_over_period
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return None


def calculate_correlation_coefficient_for_top_stock_over_period(
    filtered_prices, top_stock_filtered_prices
):
    df = pd.DataFrame([filtered_prices, top_stock_filtered_prices]).T
    return df.corr().iloc[0, 1]


def save_analysis_results_to_db(symbol, combined_analysis, correlation_dict_key_str):
    """
    Save the analysis results to the stock_analysis table.
    """
    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            for category, category_results in combined_analysis.items():
                for analysis_type, analysis_results in category_results.items():
                    top_stock_symbol = (
                        analysis_type.replace(correlation_dict_key_str, "")
                        if correlation_dict_key_str in analysis_type
                        else None
                    )
                    for period, value in analysis_results.items():
                        insert_or_update_analysis_in_db(
                            cursor,
                            symbol,
                            top_stock_symbol,
                            category,
                            analysis_type,
                            period,
                            value,
                        )
            conn.commit()
            logging.info("Analysis data saved successfully to the database.")
        except sqlite3.Error as e:
            logging.error(f"Error saving analysis data to database: {e}")


def insert_or_update_analysis_in_db(
    cursor, symbol, top_stock_symbol, category, analysis_type, period, value
):
    """
    Insert or update a stock analysis entry in the database.
    """
    cursor.execute(
        """
        SELECT 1 FROM stock_analysis
        WHERE symbol = ? AND category = ? AND analysis_type = ? AND period = ?
        """,
        (symbol, category, analysis_type, period),
    )
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO stock_analysis (symbol, top_stock_symbol, category, analysis_type, period, value)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (symbol, top_stock_symbol, category, analysis_type, period, value),
        )
    else:
        cursor.execute(
            """
            UPDATE stock_analysis
            SET value = ?
            WHERE symbol = ? AND category = ? AND analysis_type = ? AND period = ?
            """,
            (value, symbol, category, analysis_type, period),
        )
