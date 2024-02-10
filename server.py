from flask import Flask, request, jsonify
from datetime import datetime, timezone


from knackly_api import KnacklyAPI
from mongo_db import MongoDB
from config import (
    WEBHOOK_HEADER_NAME,
    WEBHOOK_HEADER_VALUE,
    ACCESS_KEY,
    ACCESS_SECRET,
    TENANCY,
    mongo_db,
)


app = Flask(__name__)
api_client = KnacklyAPI(ACCESS_KEY, ACCESS_SECRET, TENANCY)
mongo_client = MongoDB(
    mongo_db["username"],
    mongo_db["password"],
    mongo_db["cluster"],
    database_name="LightningDocs",
)


@app.route("/", methods=["POST"])
def handle_webhook():
    # If the POST request does not include a special header value, reject it
    special_header = request.headers.get(WEBHOOK_HEADER_NAME)
    if special_header is None or special_header != WEBHOOK_HEADER_VALUE:
        return jsonify({"message": "Unauthorized access"}), 401

    # Get the JSON data sent by the webhook
    event_data = request.json
    current_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)
    event_data["creationDate"] = (
        current_datetime.isoformat(timespec="milliseconds") + "Z"
    )

    # Handle the webhook data as needed
    # print(f"Received webhook data: {event_data}")

    record_data = api_client.get_record_details(
        record_id=event_data["record"], catalog=event_data["catalog"]
    )

    # "id" and "app" already in events collection?
    events_query = {"record": event_data["record"], "app": event_data["app"]}
    if mongo_client.find("test_Events", events_query):
        pass  # Do something
    else:
        pass  # Do something else

    # Insert the webhook data into our events database
    mongo_client.insert(collection="test_Events", document=event_data)

    # Respond with a success message
    return jsonify({"message": "Webhook received successfully"}), 200


def main():
    print("Hello World")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
