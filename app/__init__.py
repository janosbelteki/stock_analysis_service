import os

from flask import Flask

from app.db_config import DB_PATH, init_db
from app.logging_config import configure_logging


def create_app():
    app = Flask(__name__)
    configure_logging()

    if not os.path.exists(DB_PATH):
        init_db()

    return app
