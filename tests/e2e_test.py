import tarfile
import unittest

from io import BytesIO
from pathlib import Path


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
            print(f"Failed to load {collection_name} data:")
            print(exec_result.output.decode())
            exit(1)
        else:
            print(f"{collection_name.capitalize()} data loaded successfully!")

    def load_cities_data(self, mongo):
        self.__load_data(mongo, "cities", "cities.json")

    def load_inventories_data(self, mongo):
        self.__load_data(mongo, "inventories", "inventories.json")

    def load_users_data(self, mongo):
        self.__load_data(mongo, "users", "users.json")