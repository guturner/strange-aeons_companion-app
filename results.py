class BuildInventoryTableSuccess:
    def __init__(self, table):
        self.table = table

class BuildInventoryTableChunksSuccess:
    def __init__(self, table_chunks):
        self.table_chunks = table_chunks

class BuildTableSuccess:
    def __init__(self, table):
        self.table = table

class BuildTableChunksSuccess:
    def __init__(self, table_chunks):
        self.table_chunks = table_chunks

class LookupCitySuccess:
    def __init__(self, city):
        self.city = city

class LookupCityFailure:
    def __init__(self, city_name):
        self.message = f"City with city_name: {city_name} was not found."

class LookupItemsSuccess:
    def __init__(self, items):
        self.items = items

class LookupItemsFailure:
    def __init__(self, items):
        self.message = f"Items with item_type: {items} were not found."

class LookupMerchantSuccess:
    def __init__(self, merchant):
        self.merchant = merchant

class LookupMerchantFailure:
    def __init__(self, city_name, merchant_name):
        self.message = f"Merchant in city_name={city_name} with merchant_name: {merchant_name} was not found."

class LookupUserSuccess:
    def __init__(self, user):
        self.user = user

class LookupUserFailure:
    def __init__(self, user_id=None, username=None):
        if user_id is None:
            self.message = f"User with username: {username} was not found."
        else:
            self.message = f"User with user_id: {user_id} was not found."

class UpdateUserSuccess:
    def __init__(self, user):
        self.user = user

class UpdateUserFailure:
    def __init__(self, user_id=None, username=None):
        self.message = f"Failed to update User via user_id={user_id} and username={username}."