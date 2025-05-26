import json

from daos.dao import DAO
from mappers.inventory_mapper import InventoryMapper


def _build_filter(base_filter, additional_filter):
    if additional_filter is not None:
        return {"$and" : [base_filter, json.loads(additional_filter)]}
    else:
        return base_filter

class InventoryDao(DAO):
    def __init__(self, database):
        super().__init__(database)

    def get_general_goods(self, additional_filter):
        result = self._db["inventories"].find(_build_filter({"type" : "general_good"}, additional_filter))
        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_weapons(self, additional_filter):
        result = self._db["inventories"].find(_build_filter({"$or" : [{"type" : "melee_weapon"}, {"type" : "ranged_weapon"}]}, additional_filter))
        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_armor(self, additional_filter):
        result = self._db["inventories"].find(_build_filter({"type" : "armor"}, additional_filter))
        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))