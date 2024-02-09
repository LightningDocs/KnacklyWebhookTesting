import requests


class KnacklyAPI:
    def __init__(self, key_id: str, secret: str, tenancy: str):
        self.key_id = key_id
        self.secret = secret
        self.tenancy = tenancy
        self.base_url = f"https://api.test.go.knackly.io/{tenancy}/api/v1"
        self.authorization_header = {
            "Authorization": f"Bearer {self.get_access_token() }"
        }

    def get_access_token(self) -> str:
        """Get an access token needed for other Knackly API requests.

        Returns:
            str: A long string that will act as the access token for further API requests.
        """
        url = f"{self.base_url}/auth/login"
        payload = {"KeyID": self.key_id, "Secret": self.secret}
        r = requests.post(url, data=payload)
        return r.json()["token"]

    def get_webhooks(self) -> list[dict]:
        """Get all the currently registered webhooks.

        Returns:
            list[dict]: All of the currently registered webhooks.
        """
        url = f"{self.base_url}/webhooks"
        r = requests.get(url, headers=self.authorization_header)
        return r.json()

    def unregister_webhook(self, id: str):
        """Removes a current webhook from the API

        Args:
            id (str): The id of the webhook. Can see a list of valid id's by using self.get_webhooks()
        """
        url = f"{self.base_url}/webhooks/{id}"
        r = requests.delete(url, headers=self.authorization_header)
        return r.json()

    def unregister_all_webhooks(self):
        """Removes all currently active webhooks from the API"""
        current_webhooks = self.get_webhooks()
        for wh in current_webhooks:
            id = wh["id"]
            self.unregister_webhook(id)

    def register_webhook(
        self,
        webhook_url: str,
        events: list[str],
        catalogs: list[str],
        custom_headers: dict = None,
    ):
        """Registers a webhook with the API

        Args:
            url (str): The HTTPS server to which the webhook will post data to
            events (list[str]): Each element is a string with the name of an event you want to be notified of. Currently only supports "catalog.app.completed"
            catalogs (list[str]): Each element is a string with the name of the catalog that this webhook shouhld fire on. Optionally, just sending the one element list ["all"] will indicate all catalogs
            custom_headers: (dict): Optional python object where each key is a valid name for an HTTP header, and the value is a string that Knackly will send with that header
        """
        url = f"{self.base_url}/webhooks"
        payload = {"url": webhook_url, "events": events, "catalogs": catalogs}
        if custom_headers:
            payload["customHeaders"] = custom_headers

        r = requests.post(url, headers=self.authorization_header, json=payload)
        self.pretty_print_request_details(r.request)

        if r.status_code == 400:
            raise RuntimeError(f"something went wrong: {r.text}")
        elif r.status_code == 403:
            raise RuntimeError(f"something went wrong: {r.text}")
        return r.json()

    def get_record_details(self, record_id: str, catalog: str) -> dict:
        """Query's the Knackly API for information regarding a specific record

        Args:
            record_id (str): The unique id of the record, typically gotten from a webhook event firing
            catalog (str): The catalog that the record resides in

        Returns:
            dict: A python object containing information about the record
        """
        url = f"{self.base_url}/catalogs/{catalog}/items/{record_id}"
        r = requests.get(url, headers=self.authorization_header)
        return r.json()

    def pretty_print_request_details(self, req: requests.Request) -> None:
        """Helper function to print out the full information that python is sending to the server

        Args:
            req (requests.Request): A python Request object
        """
        print(
            "{}\n{}\r\n{}\r\n\r\n{}".format(
                "-----------START-----------",
                req.method + " " + req.url,
                "\r\n".join("{}: {}".format(k, v) for k, v in req.headers.items()),
                req.body,
            )
        )
