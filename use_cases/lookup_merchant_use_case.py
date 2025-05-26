from results import LookupCitySuccess, LookupMerchantFailure, LookupMerchantSuccess


class LookupMerchantUseCase:
    def __init__(self, lookup_city_use_case):
        self.__lookup_city_use_case = lookup_city_use_case

    def lookup_merchant_by_city_name_and_merchant_name(self, city_name, merchant_name):
        lookup_city_result = self.__lookup_city_use_case.lookup_city_by_city_name(city_name)
        match lookup_city_result:
            case LookupCitySuccess(city=found_city):
                merchant = next((merchant for merchant in found_city.merchants if merchant.name.lower() == merchant_name.lower()), None) if found_city else None
                if merchant is not None:
                    return LookupMerchantSuccess(merchant)
        return LookupMerchantFailure(city_name=city_name, merchant_name=merchant_name)