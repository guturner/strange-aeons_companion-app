class LookupCityUseCase:
    def __init__(self, city_dao):
        self.__city_dao = city_dao

    def lookup_city_by_city_name(self, city_name):
        return self.__city_dao.get_city_by_city_name(city_name)

    def lookup_cities_by_discord_user_id(self, discord_user_id: int):
        return self.__city_dao.get_cities_by_occupant_discord_user_id(discord_user_id)
