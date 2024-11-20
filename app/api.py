from flask import Flask, jsonify, request
from app.logging_config import configure_logging
import logging

configure_logging()

app = Flask(__name__)

@app.route("/collect", methods=["POST"])
def collect_data():
    identifier = request.json.get("identifier")
    try:
        data = fetch_stock_data(identifier) # To be implemented
        if data:
            save_to_db(identifier, data) # To be implemented
        else:
            logging.warning(f"No data returned for identifier: {identifier}")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Data collected successfully.",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400