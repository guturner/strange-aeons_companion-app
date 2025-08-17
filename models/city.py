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
        return f"{self.question}\n\n{self.answer}\n    {"\n    ".join(f"{merchant.name} ({merchant.description})" for merchant in merchants)}"

class Merchant:
    def __init__(self, merchant_id, name, description, sells_item_types, custom_items, number_of_table_rows):
        self.merchant_id = merchant_id
        self.name = name
        self.description = description
        self.sells_item_types = sells_item_types
        self.custom_items = custom_items
        self.number_of_table_rows = number_of_table_rows