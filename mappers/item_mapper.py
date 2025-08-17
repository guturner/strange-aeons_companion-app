from models.item import Item, SellsItemType


def _get_or_none(database_result, key):
    try:
        return database_result[key]
    except KeyError:
        return None

class ItemMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_item(self):
        return Item(
            item_type=_get_or_none(self.database_result, "type"),
            name=_get_or_none(self.database_result, "name"),
            cost=_get_or_none(self.database_result, "cost"),
            size=_get_or_none(self.database_result, "size"),
            armor_bonus=_get_or_none(self.database_result, "armorBonus"),
            max_dexterity=_get_or_none(self.database_result, "maxDexterity"),
            armor_check_penalty=_get_or_none(self.database_result, "armorCheckPenalty"),
            damage=_get_or_none(self.database_result, "damage"),
            crit_range=_get_or_none(self.database_result, "critRange"),
            delay=_get_or_none(self.database_result, "delay"),
            stats=_get_or_none(self.database_result, "stats"),
            song_instrument=_get_or_none(self.database_result, "songInstrument"),
            spell_level=_get_or_none(self.database_result, "spellLevel"),
            spell_description=_get_or_none(self.database_result, "spellDescription")
        )

class SellsItemTypeMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_sells_item_type(self):
        return SellsItemType(
            item_type=_get_or_none(self.database_result, "itemType"),
            and_filter=_get_or_none(self.database_result, "andFilter")
        )