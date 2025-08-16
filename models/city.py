class City:
    def __init__(self, city_id, name, directions, merchants, occupants):
        self.city_id = city_id
        self.name = name
        self.directions = directions
        self.merchants = merchants
        self.occupants = occupants

    def is_user_in_city(self, user_id):
        return user_id in self.occupants

class Directions:
    def __init__(self, question, answer, not_found):
        self.question = question
        self.answer = answer
        self.not_found = not_found

    def get_directions_string(self, merchants):
        return f"{self.question}\n\n{self.answer}\n    {"\n    ".join(f"{merchant.name} ({merchant.merchant_type})" for merchant in merchants)}"

class Merchant:
    def __init__(self, merchant_id, name, merchant_type, introductions, sells_armor, sells_general_goods, sells_instruments, sells_jewelry, sells_songs, sells_spells, sells_weapons, inventory, table_rows):
        self.merchant_id = merchant_id
        self.name = name
        self.merchant_type = merchant_type
        self.introductions = introductions
        self.sells_armor = sells_armor
        self.sells_general_goods = sells_general_goods
        self.sells_instruments = sells_instruments
        self.sells_jewelry = sells_jewelry
        self.sells_songs = sells_songs
        self.sells_spells = sells_spells
        self.sells_weapons = sells_weapons
        self.inventory = inventory
        self.table_rows = table_rows

class InventoryType:
    def __init__(self, enabled, override_filter):
        self.enabled = enabled
        self.override_filter = override_filter