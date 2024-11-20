import sqlite3
from contextlib import contextmanager


@contextmanager
def get_db_connection(db_path):
    """
    Context manager for SQLite database connections.
    Ensures proper opening and closing of db connection.
    """
    conn = sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    try:
        yield conn
    finally:
        conn.close()
