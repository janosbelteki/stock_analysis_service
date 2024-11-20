from flask import Flask, jsonify, request
from app.logging_config import configure_logging
import logging
from app.data_collector import fetch_stock_data, save_to_db, get_raw_data_from_db
from app.error_handler import error_response
from app import create_app
from app.data_processor import analyze_stock_data

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
    
@app.route("/get/<symbol>", methods=["GET"])
def get_raw_data_for_symbol(symbol):
    raw_data = get_raw_data_from_db(symbol)
    return jsonify(raw_data), 200

@app.route("/analyze/<symbol>", methods=["GET"])
def analyze(symbol):
    processed_data = analyze_stock_data(symbol)
    return jsonify(processed_data), 200


if __name__ == "__main__":
    app.run(debug=True)
