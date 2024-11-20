import logging
from datetime import datetime, timedelta, timezone
import requests
from app.db_config import DB_PATH
from app.db_utils import get_db_connection
import sqlite3

def fetch_stock_data(symbol, start_date=None, end_date=None):
    """
    Fetch raw stock data from the Yahoo Finance API for the specified symbol.
    """
    logging.info(f"Fetching stock data for {symbol}...")

    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)
    if end_date is None:
        end_date = datetime.now()
    print(start_date)
    print(end_date)
    period1 = int(start_date.timestamp())
    period2 = int(end_date.timestamp())

    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history",
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            stock_data = result["indicators"]["quote"][0]

            date_data = [
                datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
                for ts in timestamps
            ]

            parsed_data = [
                {
                    "date": date_data[i],
                    "open": stock_data["open"][i],
                    "close": stock_data["close"][i],
                    "high": stock_data["high"][i],
                    "low": stock_data["low"][i],
                    "volume": stock_data["volume"][i],
                }
                for i in range(len(date_data))
            ]
            return parsed_data
    else:
        logging.error(f"Failed to fetch data for {symbol}: {response.status_code}")

def save_to_db(symbol, data):
    """
    Save raw stock data downloaded from the Yahoo Finance API to the database.
    """
    try:
        with get_db_connection(DB_PATH) as conn:
            cursor = conn.cursor()
            if data is None or len(data) == 0:
                logging.error("No valid data to save.")
                return

            for record in data:
                symbol = symbol
                date = record["date"]
                open_price = record["open"]
                close_price = record["close"]
                high_price = record["high"]
                low_price = record["low"]
                volume = record["volume"]

                if None in (
                    symbol,
                    date,
                    open_price,
                    close_price,
                    high_price,
                    low_price,
                    volume,
                ):
                    logging.warning(f"Skipping record due to None value: {record}")
                    continue

                cursor.execute(
                    """
                    INSERT INTO stock_prices (symbol, date, open_price, close_price, high_price, low_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        symbol,
                        date,
                        open_price,
                        close_price,
                        high_price,
                        low_price,
                        volume,
                    ),
                )

            conn.commit()
            logging.info("Data successfully saved to the database.")
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            logging.error(f"Data for {symbol} already exists in the database.")
        else:
            logging.error(f"Error while saving data to the database: {e}")

def get_raw_data_from_db(symbol):
    """
    Retrieve raw stock data for a specific symbol from the database.
    """
    try:
        with get_db_connection(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT date, open_price, close_price, high_price, low_price, volume
                FROM stock_prices
                WHERE symbol = ?
                ORDER BY date
            """,
                (symbol,),
            )
            rows = cursor.fetchall()

        raw_data = [
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
        return raw_data
    except sqlite3.Error as e:
        raise RuntimeError(f"Error fetching raw data for symbol {symbol}: {e}")