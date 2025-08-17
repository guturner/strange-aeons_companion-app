from mappers.item_mapper import ItemMapper, SellsItemTypeMapper
from models.city import Merchant
from models.item import ItemType


class MerchantMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_merchant(self):
        sells_item_types_result = self.database_result.get("sellsItemTypes", [])
        custom_items_result = self.database_result.get("customItems", [])

        return Merchant(
            merchant_id=self.database_result["merchantId"],
            name=self.database_result["name"],
            description=self.database_result["description"],
            sells_item_types=set(
                # Filter out unknown item types:
                filter(
                    lambda sit: sit.item_type is not ItemType.MISCELLANEOUS,
                    # Map each database result to a SellsItemType DTO:
                    map(
                        lambda sit: SellsItemTypeMapper(sit).map_to_sells_item_type(),
                        sells_item_types_result
                    )
                )
            ),
            custom_items=list(map(lambda i: ItemMapper(i).map_to_item(), custom_items_result)),
            number_of_table_rows=self.database_result["numberOfTableRows"]
        )