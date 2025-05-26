class RecipeBook:
    def __init__(self, build_inventory_table_use_case, build_table_use_case, lookup_city_use_case, lookup_inventory_use_case, lookup_merchant_use_case, lookup_user_use_case, update_user_use_case):
        self.build_inventory_table = build_inventory_table_use_case
        self.build_table = build_table_use_case
        self.lookup_city = lookup_city_use_case
        self.lookup_inventory = lookup_inventory_use_case
        self.lookup_merchant = lookup_merchant_use_case
        self.lookup_user = lookup_user_use_case
        self.update_user = update_user_use_case