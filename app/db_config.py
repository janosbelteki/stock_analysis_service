import yaml
import logging
import sqlite3
from app.db_utils import get_db_connection

TABLE_SCHEMAS = {
    "stock_prices": """
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            date DATE,
            open_price REAL,
            close_price REAL,
            high_price REAL,
            low_price REAL,
            volume REAL,
            UNIQUE(symbol, date)
        )
    """,
    "stock_analysis": """
        CREATE TABLE IF NOT EXISTS stock_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            top_stock_symbol TEXT,
            category TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            period INTEGER NOT NULL,
            value REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, category, analysis_type, period)
        )
    """
}

def validate_config(config: dict) -> None:
    required_keys = ["db_path"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    validate_config(config)

DB_PATH = config["db_path"]

def init_db() -> None:
    try:
        logging.info("Initializing database...")
        with get_db_connection(DB_PATH) as conn:
            cursor = conn.cursor()
            for table_name, schema in TABLE_SCHEMAS.items():
                cursor.execute(schema)
                logging.info(f"Ensured table '{table_name}' exists.")
            conn.commit()
        logging.info(f"Database initialized successfully: {DB_PATH} created.")
    except sqlite3.Error as db_error:
        logging.error(f"Error during database initialization: {db_error}")
        raise
    except Exception as general_error:
        logging.error(
            f"Unexpected error during database initialization: {general_error}"
        )
        raise
