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
    event_data["LD_createdDate"] = (
        current_datetime.isoformat(timespec="milliseconds") + "Z"
    )

    # Handle the webhook data as needed
    print(f"Received webhook data: {event_data}")

    knackly_record = api_client.get_record_details(
        record_id=event_data["record"], catalog=event_data["catalog"]
    )
    # pprint(knackly_record)
    # print()
    knackly_record["LD_catalog"] = event_data["catalog"]

    # record "id" already in mongo records collection?
    records_query = {"id": event_data["record"]}
    previous_record = mongo_client.find("Records", records_query)
    if previous_record:
        knackly_record = copy_created_dates(previous_record, knackly_record)

    modified_knackly_record = inject_created_date(
        document=knackly_record,
        app_name=event_data["app"],
        created_date=current_datetime.isoformat(timespec="milliseconds") + "Z",
    )
    modified_knackly_record = inject_user_type(
        document=modified_knackly_record,
        app_name=event_data["app"],
        user_type=event_data["userType"],
    )

    # Insert the webhook data into our events database
    mongo_client.insert(collection="Events", document=event_data)

    # Insert the record data into our records database
    mongo_client.replace(
        collection="Records",
        document=modified_knackly_record,
        filter={"id": modified_knackly_record["id"]},
    )

    # Respond with a success message
    return jsonify({"message": "Webhook received successfully"}), 200


def copy_created_dates(previous_document: dict, new_document: dict) -> dict:
    """Copies the created dates from a previous document into a new document.

    Args:
        previous_document (dict): A Knackly record document
        new_document (dict): A Knackly record document

    Returns:
        dict: The new, modified document.
    """
    date_map = {
        app["name"]: app.get("LD_createdDate") for app in previous_document["apps"]
    }

    # Iterate through the apps in the new dict
    for app in new_document["apps"]:
        # If the app name exists in the date_map, update the LD_creationDate in the new document
        if app["name"] in date_map and date_map[app["name"]] is not None:
            app["LD_createdDate"] = date_map[app["name"]]

    return new_document


def inject_created_date(document: dict, app_name: str, created_date: str) -> dict:
    """Injects a single created date for a specific app into a document. If there already existed one for the provided app, do nothing.

    Args:
        document (dict): The entire knackly document
        app_name (str): The name of the app
        created_date (str): The created_date, formatted as an ISO string

    Returns:
        dict: The newly modified document
    """
    for app in document["apps"]:
        if app["name"] == app_name:
            # Only "inject" if there wasn't already an LD_createdDate
            if app.get("LD_createdDate") is None:
                app["LD_createdDate"] = created_date
            return document
    raise IndexError(
        f"No app found with name {app_name}. Found apps were {','.join([app['name'] for app in document['apps']])}"
    )


def inject_user_type(document: dict, app_name: str, user_type: str) -> dict:
    """Injects the provided user_type (regular/external/api) into a specific app for a document. If there already existed one for the provided app, do nothing.

    Args:
        document (dict): The entire knackly document
        app_name (str): The name of the app to apply the user_type to
        user_type (str): The type of user that ran the app. Either 'regular', 'external', or'api'

    Returns:
        dict: The newly modified document
    """
    for app in document["apps"]:
        if app["name"] == app_name:
            # Only "inject" if there wasn't already an LD_userType
            if app.get("LD_userType") is None:
                app["LD_userType"] = user_type
            return document
    raise IndexError(
        f"No app found with name {app_name}. Found apps were {','.join([app['name'] for app in document['apps']])}"
    )


def main():
    print("Hello World")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
