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
