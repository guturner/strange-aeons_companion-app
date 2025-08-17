import json

from daos.dao import DAO
from mappers.item_mapper import ItemMapper
from models.item import ItemType


class ItemDAO(DAO):
    def __init__(self, database):
        super().__init__(database)

    def get_items_by_item_type(self, item_type, override_filter):
        if item_type == ItemType.MISCELLANEOUS:
            all_item_types = [it.name.lower() for it in ItemType if it != ItemType.MISCELLANEOUS] # except MISCELLANEOUS
            base_filter = {"type" : {"$nin" : all_item_types}}
        else:
            base_filter = {"type": item_type.name.lower()}

        if override_filter is None:
            result = self._db["items"].find(base_filter)
        else:
            result = self._db["items"].find({"$and" : [base_filter, json.loads(override_filter)]})

        return tuple(map(lambda i: ItemMapper(i).map_to_item(), result))