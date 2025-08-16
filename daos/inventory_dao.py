import json

from daos.dao import DAO
from mappers.inventory_mapper import InventoryMapper


class InventoryDAO(DAO):
    def __init__(self, database):
        super().__init__(database)

    def get_armor(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type" : "armor"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_general_goods(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type": "general_good"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_instruments(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type": "instrument"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_jewelry(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type" : "jewelry"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_songs(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type": "song"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_spells(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"type": "spell"})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))

    def get_weapons(self, override_filter):
        if override_filter is None:
            result = self._db["inventories"].find({"$or" : [{"type" : "melee_weapon"}, {"type" : "ranged_weapon"}]})
        else:
            result = self._db["inventories"].find(json.loads(override_filter))

        return tuple(map(lambda i: InventoryMapper(i).map_to_item(), result))