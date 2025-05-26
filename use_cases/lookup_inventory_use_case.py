from results import LookupInventorySuccess


class LookupInventoryUseCase:
    def __init__(self, inventory_dao):
        self.__inventory_dao = inventory_dao

    def lookup_general_goods_inventory(self, inventory_filter):
        general_goods_inventory = self.__inventory_dao.get_general_goods(inventory_filter)
        return LookupInventorySuccess(general_goods_inventory)

    def lookup_weapons_inventory(self, inventory_filter):
        weapons_inventory = self.__inventory_dao.get_weapons(inventory_filter)
        return LookupInventorySuccess(weapons_inventory)

    def lookup_armor_inventory(self, inventory_filter):
        armor_inventory = self.__inventory_dao.get_armor(inventory_filter)
        return LookupInventorySuccess(armor_inventory)

    def lookup_jewelry_inventory(self, inventory_filter):
        jewelry_inventory = self.__inventory_dao.get_jewelry(inventory_filter)
        return LookupInventorySuccess(jewelry_inventory)