import uuid

from bson import Binary, UUID_SUBTYPE

from mappers.merchant_mapper import MerchantMapper
from models.city import City, Directions


class CityMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    # TODO This can probably be resolved by standardizing between the Atlas DB config and Testcontainers config
    def map_to_city_id(self):
        city_id_val = self.database_result["cityId"]

        if isinstance(city_id_val, uuid.UUID):
            return city_id_val  # already a UUID object
        elif isinstance(city_id_val, Binary) and city_id_val.subtype == UUID_SUBTYPE:
            return uuid.UUID(bytes=city_id_val)
        elif isinstance(city_id_val, str):
            return  uuid.UUID(city_id_val)  # parse from string
        return None

    def map_to_directions(self):
        return Directions(
            question=self.database_result["directions"]["question"],
            answer=self.database_result["directions"]["answer"],
            not_found=self.database_result["directions"]["notFound"]
        )

    def map_to_city(self):
        directions = self.map_to_directions()

        merchants_result = self.database_result.get("merchants", [])
        occupants_result = self.database_result.get("occupants", [])

        return City(
            city_id=self.map_to_city_id(),
            name=self.database_result["name"],
            directions=directions,
            merchants=list(map(lambda m: MerchantMapper(m).map_to_merchant(), merchants_result)),
            occupants=occupants_result
        )