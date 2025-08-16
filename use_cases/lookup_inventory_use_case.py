from results import LookupInventorySuccess


class LookupInventoryUseCase:
    def __init__(self, inventory_dao):
        self.__inventory_dao = inventory_dao

    def lookup_armor_inventory(self, override_filter):
        armor_inventory = self.__inventory_dao.get_armor(override_filter)
        return LookupInventorySuccess(armor_inventory)

    def lookup_general_goods_inventory(self, override_filter):
        general_goods_inventory = self.__inventory_dao.get_general_goods(override_filter)
        return LookupInventorySuccess(general_goods_inventory)

    def lookup_instruments_inventory(self, override_filter):
        instruments_inventory = self.__inventory_dao.get_instruments(override_filter)
        return LookupInventorySuccess(instruments_inventory)

    def lookup_jewelry_inventory(self, override_filter):
        jewelry_inventory = self.__inventory_dao.get_jewelry(override_filter)
        return LookupInventorySuccess(jewelry_inventory)

    def lookup_songs_inventory(self, override_filter):
        songs_inventory = self.__inventory_dao.get_songs(override_filter)
        return LookupInventorySuccess(songs_inventory)

    def lookup_spells_inventory(self, override_filter):
        spells_inventory = self.__inventory_dao.get_spells(override_filter)
        return LookupInventorySuccess(spells_inventory)

    def lookup_weapons_inventory(self, override_filter):
        weapons_inventory = self.__inventory_dao.get_weapons(override_filter)
        return LookupInventorySuccess(weapons_inventory)