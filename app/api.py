from flask import Flask, jsonify, request
from app.logging_config import configure_logging
import logging
from app.data_collector import fetch_stock_data, save_to_db
from app.error_handler import error_response
from app import create_app

app = create_app()

@app.route("/collect", methods=["POST"])
def collect_data():
    symbols = request.json.get("symbols")

    if not symbols or not isinstance(symbols, list):
        return error_response("Invalid input. Please provide a list of symbols.", 400)

    try:
        for symbol in symbols:
            data = fetch_stock_data(symbol)
            if data:
                save_to_db(symbol, data)
            else:
                logging.warning(f"No data returned for symbol: {symbol}")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Data collected successfully for all symbols.",
                }
            ),
            200,
        )
    except Exception as e:
        return error_response(str(e), 400)