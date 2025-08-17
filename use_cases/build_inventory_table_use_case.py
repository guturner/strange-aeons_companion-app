from models.item import ItemType
from results import LookupMerchantSuccess, LookupMerchantFailure, LookupItemsSuccess, BuildInventoryTableSuccess, \
    BuildInventoryTableChunksSuccess


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

class BuildInventoryTableUseCase:
    def __init__(self, lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case):
        self.__lookup_merchant_use_case = lookup_merchant_use_case
        self.__lookup_inventory_use_case = lookup_inventory_use_case
        self.__build_table_use_case = build_table_use_case

    def build_merchant_inventory_table(self, city_name, merchant_name):
        lookup_merchant_result = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(city_name=city_name, merchant_name=merchant_name)
        match lookup_merchant_result:
            case LookupMerchantSuccess(merchant=found_merchant):
                sells_item_types = set(map(lambda sells_item_type: sells_item_type.item_type, found_merchant.sells_item_types))
                sells_item_type_and_filters = dict(map(lambda sells_item_type: (sells_item_type.item_type, sells_item_type.and_filter), found_merchant.sells_item_types))

                has_armor = ItemType.ARMOR in sells_item_types
                has_general_good = ItemType.GENERAL_GOOD in sells_item_types
                has_instrument = ItemType.INSTRUMENT in sells_item_types
                has_jewelry = ItemType.JEWELRY in sells_item_types
                has_song = ItemType.SONG in sells_item_types
                has_spell = ItemType.SPELL in sells_item_types
                has_melee_weapon = ItemType.MELEE_WEAPON in sells_item_types
                has_ranged_weapon = ItemType.RANGED_WEAPON in sells_item_types

                custom_item_types = set(map(lambda custom_item: custom_item.item_type, found_merchant.custom_items))

                has_custom_armor = ItemType.ARMOR in custom_item_types
                has_custom_instrument = ItemType.INSTRUMENT in custom_item_types
                has_custom_melee_weapon = ItemType.MELEE_WEAPON in custom_item_types
                has_custom_ranged_weapon = ItemType.RANGED_WEAPON in custom_item_types
                has_custom_misc_item = ItemType.MISCELLANEOUS in custom_item_types

                display_armor_columns = has_armor or has_custom_armor
                display_songs_columns = has_song
                display_spell_columns = has_spell
                display_weapon_columns = has_melee_weapon or has_ranged_weapon or has_custom_melee_weapon or has_custom_ranged_weapon
                display_instrument_columns = has_instrument or has_custom_instrument

                custom_items_data = _generate_inventory_tuples(
                    found_merchant.custom_items,
                    armor=display_armor_columns,
                    instruments=display_instrument_columns,
                    songs=display_songs_columns,
                    spells=display_spell_columns,
                    weapons=display_weapon_columns,
                    misc_items=has_custom_misc_item
                ) if found_merchant.custom_items else ()

                armor_inventory_data = _get_inventory_data(
                    has_armor,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.ARMOR, sells_item_type_and_filters[ItemType.ARMOR]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                general_goods_inventory_data = _get_inventory_data(
                    has_general_good,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.GENERAL_GOOD, sells_item_type_and_filters[ItemType.GENERAL_GOOD]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                instruments_inventory_data = _get_inventory_data(
                    has_instrument,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.INSTRUMENT, sells_item_type_and_filters[ItemType.INSTRUMENT]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                jewelry_inventory_data = _get_inventory_data(
                    has_jewelry,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.JEWELRY, sells_item_type_and_filters[ItemType.JEWELRY]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                songs_inventory_data = _get_inventory_data(
                    has_song,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.SONG, sells_item_type_and_filters[ItemType.SONG]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                spells_inventory_data = _get_inventory_data(
                    has_spell,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.SPELL, sells_item_type_and_filters[ItemType.SPELL]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                melee_weapons_inventory_data = _get_inventory_data(
                    has_melee_weapon,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.MELEE_WEAPON, sells_item_type_and_filters[ItemType.MELEE_WEAPON]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                ranged_weapons_inventory_data = _get_inventory_data(
                    has_ranged_weapon,
                    lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.RANGED_WEAPON, sells_item_type_and_filters[ItemType.RANGED_WEAPON]),
                    armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns,
                    weapons=display_weapon_columns, misc_items=has_custom_misc_item
                )

                headers = _generate_inventory_header(armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)

                rows = general_goods_inventory_data + instruments_inventory_data + songs_inventory_data + spells_inventory_data + melee_weapons_inventory_data + ranged_weapons_inventory_data + armor_inventory_data + jewelry_inventory_data + custom_items_data
                rows = tuple(sorted(list(rows), key=lambda row: row[0]))

                max_rows = found_merchant.number_of_table_rows

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