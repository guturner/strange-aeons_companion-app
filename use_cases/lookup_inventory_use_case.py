from models.item import ItemType
from results import LookupItemsSuccess


class LookupItemsUseCase:
    def __init__(self, item_dao):
        self.__inventory_dao = item_dao

    def lookup_armor_inventory(self, override_filter):
        armor_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.ARMOR, override_filter)
        return LookupItemsSuccess(armor_inventory)

    def lookup_general_goods_inventory(self, override_filter):
        general_goods_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.GENERAL_GOOD, override_filter)
        return LookupItemsSuccess(general_goods_inventory)

    def lookup_instruments_inventory(self, override_filter):
        instruments_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.INSTRUMENT, override_filter)
        return LookupItemsSuccess(instruments_inventory)

    def lookup_jewelry_inventory(self, override_filter):
        jewelry_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.JEWELRY, override_filter)
        return LookupItemsSuccess(jewelry_inventory)

    def lookup_songs_inventory(self, override_filter):
        songs_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.SONG, override_filter)
        return LookupItemsSuccess(songs_inventory)

    def lookup_spells_inventory(self, override_filter):
        spells_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.SPELL, override_filter)
        return LookupItemsSuccess(spells_inventory)

    def lookup_weapons_inventory(self, override_filter):
        melee_weapons_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.MELEE_WEAPON, override_filter)
        ranged_weapons_inventory = self.__inventory_dao.get_items_by_item_type(ItemType.RANGED_WEAPON, override_filter)
        return LookupItemsSuccess(melee_weapons_inventory + ranged_weapons_inventory)