from results import LookupMerchantSuccess, LookupMerchantFailure, LookupInventorySuccess, BuildInventoryTableSuccess, \
    BuildInventoryTableChunksSuccess


def _generate_inventory_header(armor=False, weapons=False):
    base_headers = ("NAME", "TYPE", "COST")
    armor_headers = ("AC", "MAX DEX", "ACP") if armor else ()
    weapon_headers = ("DMG", "CRIT", "DELAY") if weapons else ()
    stats_headers = ("SIZE", "STATS",) if armor or weapons else ()

    return base_headers + armor_headers + weapon_headers + stats_headers

def _generate_inventory_tuple(item, armor=False, weapons=False):
    base_values = (item.name, item.item_type, item.cost)
    armor_values = (item.armor_bonus, item.max_dexterity, item.armor_check_penalty) if armor else ()
    weapon_values = (item.damage, item.crit_range, item.delay) if weapons else ()
    stats_values = (item.size, item.stats) if armor or weapons else ()

    return base_values + armor_values + weapon_values + stats_values

def _generate_inventory_tuples(items, armor=False, weapons=False):
    return tuple(map(lambda item: _generate_inventory_tuple(item, armor, weapons), items))

def _get_inventory_data(should_lookup: bool, lookup_fn, armor=False, weapons=False):
    if not should_lookup:
        return ()

    result = lookup_fn()
    if isinstance(result, LookupInventorySuccess):
        return _generate_inventory_tuples(items=result.inventory, armor=armor, weapons=weapons)
    return ()

class BuildInventoryTableUseCase:
    def __init__(self, lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case):
        self.__lookup_merchant_use_case = lookup_merchant_use_case
        self.__lookup_inventory_use_case = lookup_inventory_use_case
        self.__build_table_use_case = build_table_use_case

    def build_merchant_inventory_table(self, city_name, merchant_name):
        lookup_merchant_result = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(city_name=city_name, merchant_name=merchant_name)
        match lookup_merchant_result:
            case LookupMerchantSuccess(merchant=found_merchant):
                headers = _generate_inventory_header(found_merchant.sells_armor.enabled, found_merchant.sells_weapons.enabled)

                inventory_data = _generate_inventory_tuples(found_merchant.inventory, found_merchant.sells_armor.enabled, found_merchant.sells_weapons.enabled) if found_merchant.inventory else ()

                sells_general_goods = found_merchant.sells_general_goods.enabled
                general_goods_filter = found_merchant.sells_general_goods.inventory_filter

                sells_weapons = found_merchant.sells_weapons.enabled
                weapons_filter = found_merchant.sells_weapons.inventory_filter

                sells_armor = found_merchant.sells_armor.enabled
                armor_filter = found_merchant.sells_armor.inventory_filter

                general_goods_inventory_data = _get_inventory_data(
                    sells_general_goods,
                    lambda: self.__lookup_inventory_use_case.lookup_general_goods_inventory(general_goods_filter),
                    sells_armor, sells_weapons
                )

                weapons_inventory_data = _get_inventory_data(
                    sells_weapons,
                    lambda: self.__lookup_inventory_use_case.lookup_weapons_inventory(weapons_filter),
                    sells_armor, sells_weapons
                )

                armor_inventory_data = _get_inventory_data(
                    sells_armor,
                    lambda: self.__lookup_inventory_use_case.lookup_armor_inventory(armor_filter),
                    sells_armor, sells_weapons
                )

                rows = general_goods_inventory_data + weapons_inventory_data + armor_inventory_data + inventory_data

                build_table_chunks_result = self.__build_table_use_case.build_ascii_table_chunks(headers, rows, max_rows=10)
                inventory_table_chunks = build_table_chunks_result.table_chunks
                if len(inventory_table_chunks) == 1:
                    return BuildInventoryTableSuccess(table=f"```{found_merchant.name}'s Inventory:\n{inventory_table_chunks[0]}```")
                else:
                    table_chunks = []
                    for index, chunk in enumerate(inventory_table_chunks):
                        table_chunks.append(f"```{found_merchant.name}'s Inventory (Part {index + 1} / {len(inventory_table_chunks)}):\n{inventory_table_chunks[index]}```")
                    return BuildInventoryTableChunksSuccess(table_chunks=table_chunks)

        return LookupMerchantFailure(city_name=city_name, merchant_name=merchant_name)