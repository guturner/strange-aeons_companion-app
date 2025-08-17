from results import LookupItemsSuccess


class LookupItemsUseCase:
    def __init__(self, item_dao):
        self.__inventory_dao = item_dao

    def lookup_items_by_item_type(self, item_type, override_filter):
        inventory = self.__inventory_dao.get_items_by_item_type(item_type, override_filter)
        return LookupItemsSuccess(inventory)