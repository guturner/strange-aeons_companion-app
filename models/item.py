from enum import Enum


class ItemType(Enum):
    ARMOR = "Armor"
    GENERAL_GOOD = "General Good"
    INSTRUMENT = "Instrument"
    JEWELRY = "Jewelry"
    MISCELLANEOUS = "Miscellaneous"
    SONG = "Song"
    SPELL = "Spell"
    MELEE_WEAPON = "Melee Weapon"
    RANGED_WEAPON = "Ranged Weapon"

def get_item_type_by_input(input_string):
    try:
        return ItemType[input_string.upper()]
    except KeyError:
        return ItemType.MISCELLANEOUS

class Item:
    def __init__(self, item_type, name, cost, size, armor_bonus, armor_check_penalty, damage, crit_range, delay, max_dexterity, stats, song_instrument, spell_level, spell_description):
        self.item_type = get_item_type_by_input(item_type)
        self.name = name
        self.cost = cost
        self.size = size if size else "--"
        self.armor_bonus = armor_bonus if armor_bonus else "--"
        self.armor_check_penalty = armor_check_penalty if armor_check_penalty else "--"
        self.damage = damage if damage else "--"
        self.crit_range = crit_range if crit_range else "--"
        self.delay = delay if delay else "--"
        self.max_dexterity = max_dexterity if max_dexterity else "--"
        self.stats = stats if stats else "--"
        self.song_instrument = song_instrument if song_instrument else "--"
        self.spell_level = spell_level if spell_level else "--"
        self.spell_description = spell_description if spell_description else "--"