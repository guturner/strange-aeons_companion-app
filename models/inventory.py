from enum import Enum


class ItemType(Enum):
    ARMOR = "Armor"
    GENERAL_GOOD = "General Good"
    MELEE_WEAPON = "Weapon"
    RANGED_WEAPON = "Weapon"
    UNKNOWN = "Unknown"

def get_item_type_by_input(input_string):
    try:
        return ItemType[input_string.upper()]
    except KeyError:
        return ItemType.UNKNOWN

class Item:
    def __init__(self, item_type, name, cost, size, armor_bonus, armor_check_penalty, damage, crit_range, delay, max_dexterity, stats):
        self.item_type = get_item_type_by_input(item_type).value
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