from flask import Flask, request, jsonify
from datetime import datetime, timezone

from knackly_api import KnacklyAPI
from config import (
    WEBHOOK_HEADER_NAME,
    WEBHOOK_HEADER_VALUE,
    ACCESS_KEY,
    ACCESS_SECRET,
    TENANCY,
)

app = Flask(__name__)
api_client = KnacklyAPI(ACCESS_KEY, ACCESS_SECRET, TENANCY)


@app.route("/", methods=["POST"])
def handle_webhook():
    # If the POST request does not include a special header value, reject it
    special_header = request.headers.get(WEBHOOK_HEADER_NAME)
    if special_header is None or special_header != WEBHOOK_HEADER_VALUE:
        return jsonify({"message": "Unauthorized access"}), 401

    # Get the JSON data sent by the webhook
    data = request.json

    # Handle the webhook data as needed
    print(f"Received webhook data: {data}")

    record_data = api_client.get_record_details(
        record_id=data["record"], catalog=data["catalog"]
    )
    current_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Respond with a success message
    return jsonify({"message": "Webhook received successfully"}), 200


def main():
    print("Hello World")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
