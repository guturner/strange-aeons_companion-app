from models.city import InventoryType
from models.item import Item


def _get_or_none(database_result, key):
    try:
        return database_result[key]
    except KeyError:
        return None

class ItemTypeMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_inventory_type(self):
        return InventoryType(
            enabled=_get_or_none(self.database_result, "enabled"),
            override_filter=_get_or_none(self.database_result, "override_filter")
        )

class ItemMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_item(self):
        return Item(
            item_type=_get_or_none(self.database_result, "type"),
            name=_get_or_none(self.database_result, "name"),
            cost=_get_or_none(self.database_result, "cost"),
            size=_get_or_none(self.database_result, "size"),
            armor_bonus=_get_or_none(self.database_result, "armor_bonus"),
            max_dexterity=_get_or_none(self.database_result, "max_dexterity"),
            armor_check_penalty=_get_or_none(self.database_result, "armor_check_penalty"),
            damage=_get_or_none(self.database_result, "damage"),
            crit_range=_get_or_none(self.database_result, "critRange"),
            delay=_get_or_none(self.database_result, "delay"),
            stats=_get_or_none(self.database_result, "stats"),
            song_instrument=_get_or_none(self.database_result, "song_instrument"),
            spell_level=_get_or_none(self.database_result, "spell_level"),
            spell_description=_get_or_none(self.database_result, "spell_description")
        )