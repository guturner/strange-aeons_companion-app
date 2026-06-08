from bson import Int64

from daos.dao import DAO
from mappers.city_mapper import CityMapper


class CityDAO(DAO):
    def __init__(self, database):
        super().__init__(database)

    def get_city_by_city_name(self, city_name):
        result = self._db["cities"].find_one({"name": {"$regex": f"^{city_name}$", "$options": "i"}})
        return CityMapper(result).map_to_city() if result else None

    def get_cities_by_occupant_discord_user_id(self, discord_user_id: int):
        results = self._db["cities"].find({"occupants": Int64(discord_user_id)})
        return [CityMapper(doc).map_to_city() for doc in results]