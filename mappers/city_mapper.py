from mappers.merchant_mapper import MerchantMapper
from models.city import Directions, City


class CityMapper:
    def __init__(self, database_result):
        self.database_result = database_result

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
            city_id=self.database_result["cityId"],
            name=self.database_result["name"],
            directions=directions,
            merchants=list(map(lambda m: MerchantMapper(m).map_to_merchant(), merchants_result)),
            occupants=occupants_result
        )