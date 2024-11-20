from flask import Flask
from app.logging_config import configure_logging
import os
from app.db_config import DB_PATH, init_db

def create_app():
    app = Flask(__name__)
    configure_logging()

    if not os.path.exists(DB_PATH):
        init_db()

    return app