class LookupMerchantUseCase:
    def __init__(self, lookup_city_use_case):
        self.__lookup_city_use_case = lookup_city_use_case

    def lookup_merchant_by_city_name_and_merchant_name(self, city_name, merchant_name):
        city = self.__lookup_city_use_case.lookup_city_by_city_name(city_name)
        if city is not None:
                return next(
                    (merchant for merchant in city.merchants if merchant.name.lower() == merchant_name.lower()), None
                )
        else:
            return None