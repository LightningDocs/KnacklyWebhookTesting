import requests


import config


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

    def register_webhook(self, url: str, events: list[str], catalogs: list[str]):
        """Registers a webhook with the API

        Args:
            url (str): The HTTPS server to which the webhook will post data to
            events (list[str]): Each element is a string with the name of an event you want to be notified of. Currently only supports "catalog.app.completed"
            catalogs (list[str]): Each element is a string with the name of the catalog that this webhook shouhld fire on. Optionally, just sending the one element list ["all"] will indicate all catalogs.
        """
        url = f"{self.base_url}/webhooks"
        payload = {"url": url, "events": events, "catalogs": catalogs}
        r = requests.post(url, headers=self.authorization_header, data=payload)

        if r.status_code == 400:
            raise RuntimeError(f"something went wrong: {r.text}")
        elif r.status_code == 403:
            raise RuntimeError(f"something went wrong: {r.text}")
        return r.json()


if __name__ == "__main__":
    # Create an API client
    test_api_client = KnacklyAPI(
        key_id=config.ACCESS_KEY, secret=config.ACCESS_SECRET, tenancy=config.TENANCY
    )

    # Get all webhooks
    all_webhooks = test_api_client.get_webhooks()
    print("All webhooks:")
    for wh in all_webhooks:
        print(wh)
    if len(all_webhooks) == 0:
        print("[]")

    # Register any webhooks
    registered = test_api_client.register_webhook(
        url="https://webhook.site/9aaa1d92-f70d-4f48-b767-45fc5c04a26b",
        events=["catalog.app.completed"],
        catalogs=["MasterLoanDocs"],
    )
    print(registered)

    # Remove a webhook
    # removed = test_api_client.unregister_webhook(id="65c2d8550c89ea9f50efacef")
    # print(removed)

    # Remove all webhooks
    # test_api_client.unregister_all_webhooks()
