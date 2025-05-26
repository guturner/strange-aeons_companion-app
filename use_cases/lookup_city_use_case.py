from results import LookupCityFailure, LookupCitySuccess


class LookupCityUseCase:
    def __init__(self, city_dao):
        self.__city_dao = city_dao

    def lookup_city_by_city_name(self, city_name):
        city = self.__city_dao.get_city_by_city_name(city_name)
        if city is not None:
            return LookupCitySuccess(city)

        return LookupCityFailure(city_name)