from mappers.inventory_mapper import InventoryMapper, InventoryTypeMapper
from models.city import Merchant, InventoryType


class MerchantMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_merchant(self):
        introductions_result = self.database_result.get("introductions", [])
        inventory_result = self.database_result.get("inventory", [])

        return Merchant(
            merchant_id=self.database_result["merchantId"],
            name=self.database_result["name"],
            merchant_type=self.database_result["type"],
            introductions=introductions_result,
            sells_general_goods=InventoryTypeMapper(self.database_result["sellsGeneralGoods"]).map_to_inventory_type(),
            sells_weapons=InventoryTypeMapper(self.database_result["sellsWeapons"]).map_to_inventory_type(),
            sells_armor=InventoryTypeMapper(self.database_result["sellsArmor"]).map_to_inventory_type(),
            inventory=list(map(lambda i: InventoryMapper(i).map_to_item(), inventory_result)),
        )