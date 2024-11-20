from app.db_config import DB_PATH
from app.db_utils import get_db_connection
from datetime import datetime, timedelta
import logging
from dateutil.relativedelta import relativedelta
import pytz
from app.data_collector import fetch_stock_data, save_to_db

def analyze_stock_data(symbol: str):
    """
    Fetch data from the database and perform analysis for the specified stock symbol.
    """
    data = get_stock_data_from_db_for_last_thirty_days(symbol)
    return perform_analysis(symbol, data) # To be implemented

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
        end_date = get_last_trading_day(
            datetime.now(pytz.timezone("America/New_York"))
        )
        
        if start_date is None or start_date < end_date.date():
            logging.info(f"Fetching data for {symbol} from {start_date} to {end_date.date()}")
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