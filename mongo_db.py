import pymongo


class MongoDB:
    def __init__(
        self, username: str, password: str, cluster: str, database_name: str
    ) -> None:
        try:
            client = pymongo.MongoClient(
                f"mongodb+srv://{username}:{password}:{cluster}"
            )
            print("Successfully connected to MongoDB.")
            self._client = client
            self._db = client[database_name]
        except Exception as e:
            print(f"Something went wrong while connecting to MongoDB: {e}")

    def clear_collection(self, name: str) -> None:
        """Attempts to remove all the documents in a collection. This *does not* remove the collection itself, meaning any indexes will remain.

        Args:
            name (str): The name of the collection to clear
        """
        try:
            col = self._db[name]
            col.delete_many({})
            print(f"Successfully cleared the collection `{name}`.")
        except Exception as e:
            print(
                f"Something went wrong while trying to clear the `{name}` collection: {e}"
            )

    def drop_collection(self, name: str) -> None:
        """Attempts to completely delete a collection. This means any indexes on the collection will be lost.

        Args:
            name (str): The name of the collection to drop
        """
        try:
            col = self._db[name]
            col.drop()
            print(f"Successfully dropped the collection `{name}.`")
        except Exception as e:
            print(
                f"Something went wrong while trying to drop the `{name}` collection: {e}"
            )

    def create_new_index(
        self, field: str, sort_direction: str, collection: str
    ) -> None:
        """Create an index on a specific collection.

        Args:
            field (str): The name of the field to index on
            sort_direction (str): Whether the index should be sorted in ascending or descending order. Must be either `ASCENDING` or `DESCENDING`
            collection (str): The name of the collection that this index should be made inside of
        """
        col = self._db[collection]

        # Construct the index name
        if sort_direction not in ["ASCENDING", "DESCENDING"]:
            raise ValueError(
                f"Invalid sort direction provided: {sort_direction}. Must be either `ASCENDING` or `DESCENDING`."
            )
        sort_direction = (
            pymongo.ASCENDING if sort_direction == "ASCENDING" else pymongo.DESCENDING
        )
        index_name = f"{field}_{sort_direction}"

        # Check if the index already exists
        if index_name in col.index_information():
            raise RuntimeError(f"Index `{index_name}` already exists.")

        # If it doesn't, then create the new index
        new_index = col.create_index([(field, sort_direction)], unique=True)
        print(
            f"Successfully created new index `{new_index}` in collection `{collection}`"
        )

    def insert(self, collection: str, document: dict) -> None:
        """Inserts a document to a specific collection.

        Args:
            collection (str): The name of the collection that the document should be inserted into
            document (dict): The document itself. Should be a python dictionary object
        """
        pass

    def find(self, collection: str, query: dict) -> dict:
        """Finds and returns a single document from the collection, if possible.

        Args:
            collection (str): The name of the collection to search in
            query (dict): The query object to use in the search

        Returns:
            dict: The returned document, if one was found. Otherwise, returns `None`
        """
        col = self._db[collection]
        result = col.find_one(query)
        return result
