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
        import logging
        from bson import Int64

        logging.info(f"Querying cities for discord_user_id={discord_user_id} (type={type(discord_user_id)})")

        # Try both plain int and Int64 to see which one hits
        results_int = list(self._db["cities"].find({"occupants": discord_user_id}))
        results_int64 = list(self._db["cities"].find({"occupants": Int64(discord_user_id)}))

        logging.info(f"Results with plain int: {len(results_int)}")
        logging.info(f"Results with Int64: {len(results_int64)}")

        # Also dump one raw document to see what occupants actually looks like in Python
        sample = self._db["cities"].find_one({"name": "Kirathas"})
        if sample:
            logging.info(
                f"Kirathas occupants raw: {sample.get('occupants')} (types: {[type(x) for x in sample.get('occupants', [])]})")

        return [CityMapper(doc).map_to_city() for doc in results_int64]