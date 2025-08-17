import tarfile
import unittest

from io import BytesIO
from pathlib import Path

import pytest


def _tar_for_file(file_path: Path, file_name):
    tar_stream = BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tar.add(file_path, arcname=file_name)
    tar_stream.seek(0)
    return tar_stream.read()


class E2ETest(unittest.IsolatedAsyncioTestCase):

    def __load_data(self, mongo, collection_name, file_name):
        print(f"Starting to load {collection_name} data...")
        data_path = Path(__file__).parent.parent / "sample_data" / "mongodb" / file_name

        mongo._container.put_archive("/tmp", _tar_for_file(data_path, file_name))
        exec_result = mongo._container.exec_run([
            "mongoimport",
            "--db", "everquest",
            "--collection", collection_name,
            "--file", f"/tmp/{file_name}",
            "--mode=upsert"
        ])

        if exec_result.exit_code != 0:
            error_message = f"Failed to load {collection_name} data: {exec_result.output.decode()}"
            print(error_message)
            pytest.fail(error_message)
        else:
            print(f"{collection_name.capitalize()} data loaded successfully!")

    def initialize_user(self, mongo_client, username, user_id):
        print(f"Initializing user {username}...")
        result = mongo_client.everquest.users.update_one({"discord.username": username}, {"$set": {"userId": user_id}})
        if result.modified_count == 1:
            print(f"User {username} initialized successfully!")
        else:
            error_message = f"Failed to initialize user {username}: {result.raw_result}"
            print(error_message)
            pytest.fail(error_message)

    def set_city_occupants(self, mongo_client, city_name, occupants_list):
        print("Starting to update city occupants...")
        result = mongo_client.everquest.cities.update_one({"name" : city_name}, {"$set" : {"occupants" : occupants_list}})
        if result.modified_count == 1:
            print("City occupants updated successfully!")
        else:
            error_message = f"Failed to update city occupants: {result.raw_result}"
            print(error_message)
            pytest.fail(error_message)

    def load_cities_data(self, mongo):
        self.__load_data(mongo, "cities", "cities.json")

    def load_items_data(self, mongo):
        self.__load_data(mongo, "items", "items.json")

    def load_users_data(self, mongo):
        self.__load_data(mongo, "users", "users.json")