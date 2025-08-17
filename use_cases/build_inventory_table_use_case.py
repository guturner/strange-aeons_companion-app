from results import LookupMerchantSuccess, LookupMerchantFailure, LookupItemsSuccess, BuildInventoryTableSuccess, \
    BuildInventoryTableChunksSuccess


def _build_inventory_ledger(merchant):
    return {
        "armor" : {
            "enabled" : merchant.sells_armor.enabled,
            "override_filter" : merchant.sells_armor.override_filter
        },
        "general_goods" : {
            "enabled" : merchant.sells_general_goods.enabled,
            "override_filter" : merchant.sells_general_goods.override_filter
        },
        "instruments" : {
            "enabled" : merchant.sells_instruments.enabled,
            "override_filter" : merchant.sells_instruments.override_filter
        },
        "jewelry": {
            "enabled": merchant.sells_jewelry.enabled,
            "override_filter": merchant.sells_jewelry.override_filter
        },
        "songs": {
            "enabled": merchant.sells_songs.enabled,
            "override_filter": merchant.sells_songs.override_filter
        },
        "spells" : {
            "enabled": merchant.sells_spells.enabled,
            "override_filter": merchant.sells_spells.override_filter
        },
        "weapons": {
            "enabled": merchant.sells_weapons.enabled,
            "override_filter": merchant.sells_weapons.override_filter
        }
    }

def _generate_inventory_header(armor=False, instruments=False, songs=False, spells=False, weapons=False, misc_items=False):
    base_headers = ("NAME", "TYPE", "COST")
    armor_headers = ("AC", "MAX DEX", "ACP") if armor else ()
    song_headers = ("INSTRUMENT",) if songs else ()
    spell_headers = ("LVL", "DESCRIPTION") if songs or spells else ()
    weapon_headers = ("DMG", "CRIT", "DELAY") if weapons else ()
    stats_headers = ("SIZE", "STATS",) if armor or weapons or instruments or misc_items else ()

    return base_headers + song_headers + spell_headers + armor_headers + weapon_headers + stats_headers

def _generate_inventory_tuple(item, armor=False, instruments=False, songs=False, spells=False, weapons=False, misc_items=False):
    base_values = (item.name, item.item_type.value, item.cost)
    armor_values = (item.armor_bonus, item.max_dexterity, item.armor_check_penalty) if armor else ()
    songs_values = (item.song_instrument,) if songs else ()
    spells_values = (item.spell_level, item.spell_description) if songs or spells else ()
    weapon_values = (item.damage, item.crit_range, item.delay) if weapons else ()
    stats_values = (item.size, item.stats) if armor or weapons or instruments or misc_items else ()

    return base_values + songs_values + spells_values + armor_values + weapon_values + stats_values

def _generate_inventory_tuples(items, armor=False, instruments=False, songs=False, spells=False, weapons=False, misc_items=False):
    return tuple(map(lambda item: _generate_inventory_tuple(item, armor=armor, instruments=instruments, songs=songs, spells=spells, weapons=weapons, misc_items=misc_items), items))

def _get_inventory_data(should_lookup: bool, lookup_fn, armor=False, instruments=False, songs=False, spells=False, weapons=False, misc_items=False):
    if not should_lookup:
        return ()

    result = lookup_fn()
    if isinstance(result, LookupItemsSuccess):
        return _generate_inventory_tuples(items=result.items, armor=armor, instruments=instruments, songs=songs, spells=spells, weapons=weapons, misc_items=misc_items)
    return ()

def _has_custom_item_type(inventory, item_type):
    return any(item.item_type.name == item_type.upper() for item in inventory)

class BuildInventoryTableUseCase:
    def __init__(self, lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case):
        self.__lookup_merchant_use_case = lookup_merchant_use_case
        self.__lookup_inventory_use_case = lookup_inventory_use_case
        self.__build_table_use_case = build_table_use_case

    def build_merchant_inventory_table(self, city_name, merchant_name):
        lookup_merchant_result = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(city_name=city_name, merchant_name=merchant_name)
        match lookup_merchant_result:
            case LookupMerchantSuccess(merchant=found_merchant):
                has_custom_armor = _has_custom_item_type(found_merchant.inventory, "armor")
                has_custom_melee_weapon = _has_custom_item_type(found_merchant.inventory, "melee_weapon")
                has_custom_ranged_weapon = _has_custom_item_type(found_merchant.inventory, "ranged_weapon")
                has_custom_instrument = _has_custom_item_type(found_merchant.inventory, "instrument")
                has_custom_misc_items = _has_custom_item_type(found_merchant.inventory, "miscellaneous")

                inventory_ledger = _build_inventory_ledger(found_merchant)

                display_armor_columns = inventory_ledger["armor"]["enabled"] or has_custom_armor
                display_songs_columns = inventory_ledger["songs"]["enabled"]
                display_spell_columns = inventory_ledger["spells"]["enabled"]
                display_weapon_columns = inventory_ledger["weapons"]["enabled"] or has_custom_melee_weapon or has_custom_ranged_weapon
                display_instrument_columns = inventory_ledger["instruments"]["enabled"] or has_custom_instrument

                inventory_data = _generate_inventory_tuples(
                    found_merchant.inventory,
                    armor=display_armor_columns,
                    instruments=display_instrument_columns,
                    songs=display_songs_columns,
                    spells=display_spell_columns,
                    weapons=display_weapon_columns,
                    misc_items=has_custom_misc_items
                ) if found_merchant.inventory else ()

                armor_inventory_data = _get_inventory_data(
                    inventory_ledger["armor"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_armor_inventory(
                        inventory_ledger["armor"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                general_goods_inventory_data = _get_inventory_data(
                    inventory_ledger["general_goods"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_general_goods_inventory(inventory_ledger["general_goods"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                instruments_inventory_data = _get_inventory_data(
                    inventory_ledger["instruments"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_instruments_inventory(
                        inventory_ledger["instruments"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                jewelry_inventory_data = _get_inventory_data(
                    inventory_ledger["jewelry"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_jewelry_inventory(
                        inventory_ledger["jewelry"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                songs_inventory_data = _get_inventory_data(
                    inventory_ledger["songs"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_songs_inventory(
                        inventory_ledger["songs"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                spells_inventory_data = _get_inventory_data(
                    inventory_ledger["spells"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_spells_inventory(
                        inventory_ledger["spells"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                weapons_inventory_data = _get_inventory_data(
                    inventory_ledger["weapons"]["enabled"],
                    lambda: self.__lookup_inventory_use_case.lookup_weapons_inventory(inventory_ledger["weapons"]["override_filter"]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_items
                )

                headers = _generate_inventory_header(armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_items)

                rows = general_goods_inventory_data + instruments_inventory_data + songs_inventory_data + spells_inventory_data + weapons_inventory_data + armor_inventory_data + jewelry_inventory_data + inventory_data
                rows = tuple(sorted(list(rows), key=lambda row: row[0]))

                max_rows = found_merchant.table_rows

                build_table_chunks_result = self.__build_table_use_case.build_ascii_table_chunks(headers, rows, max_rows=max_rows)
                inventory_table_chunks = build_table_chunks_result.table_chunks
                if len(inventory_table_chunks) == 1:
                    return BuildInventoryTableSuccess(table=f"```{found_merchant.name}'s Inventory:\n{inventory_table_chunks[0]}```")
                else:
                    table_chunks = []
                    for index, chunk in enumerate(inventory_table_chunks):
                        table_chunks.append(f"```{found_merchant.name}'s Inventory (Part {index + 1} / {len(inventory_table_chunks)}):\n{inventory_table_chunks[index]}```")
                    return BuildInventoryTableChunksSuccess(table_chunks=table_chunks)

        return LookupMerchantFailure(city_name=city_name, merchant_name=merchant_name)