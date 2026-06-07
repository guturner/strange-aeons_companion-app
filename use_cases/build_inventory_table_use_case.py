import nextcord

from models.item import ItemType


# ---------------------------------------------------------------------------
# Existing ASCII helpers (unchanged)
# ---------------------------------------------------------------------------

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
    if result is not None:
        return _generate_inventory_tuples(items=result, armor=armor, instruments=instruments, songs=songs, spells=spells, weapons=weapons, misc_items=misc_items)
    return ()


# ---------------------------------------------------------------------------
# New embed helpers
# ---------------------------------------------------------------------------

# Parchment gold — fits the EverQuest aesthetic. Change freely.
_EMBED_COLOR = 0xC8A96E

# How many items to show per embed page. Discord allows up to 25 fields;
# keeping it at 5 gives breathing room and stays readable on a narrow screen.
_ITEMS_PER_PAGE = 5


def _field_value_for_item(item) -> str:
    """
    Build a compact, mobile-friendly field value for one inventory item.
    Skips any attribute that is None or empty so the embed stays clean.
    """
    def _skip(val) -> bool:
        return not val or str(val).strip() in ("", "--", "—")

    parts = []

    # Type
    if item.item_type:
        parts.append(f"**Type:** {item.item_type.value}")

    # Armor-specific
    if item.armor_bonus and not _skip(item.armor_bonus):
        parts.append(f"**AC:** {item.armor_bonus}")
    if item.max_dexterity and not _skip(item.max_dexterity):
        parts.append(f"**Max Dex:** {item.max_dexterity}")
    if item.armor_check_penalty and not _skip(item.armor_check_penalty):
        parts.append(f"**ACP:** {item.armor_check_penalty}")

    # Weapon-specific
    if item.damage and not _skip(item.damage):
        parts.append(f"**Dmg:** {item.damage}")
    if item.crit_range and not _skip(item.crit_range):
        parts.append(f"**Crit:** {item.crit_range}")
    if item.delay and not _skip(item.delay):
        parts.append(f"**Delay:** {item.delay}")

    # Song/spell
    if hasattr(item, "song_instrument") and not _skip(item.song_instrument):
        parts.append(f"**Instrument:** {item.song_instrument}")
    if hasattr(item, "spell_level") and not _skip(item.spell_level):
        parts.append(f"**Lvl:** {item.spell_level}")
    if hasattr(item, "spell_description") and not _skip(item.spell_description):
        parts.append(f"**Desc:** {item.spell_description}")

    # Shared
    if item.size and not _skip(item.size):
        parts.append(f"**Size:** {item.size}")
    if item.stats and not _skip(item.stats):
        parts.append(f"**Stats:** {item.stats}")
    if item.cost and not _skip(item.cost):
        parts.append(f"**Cost:** {item.cost}")

    return "\n".join(parts) if parts else "—"


def _build_embed_pages(merchant, items: list) -> list[nextcord.Embed]:
    """
    Chunk items into pages of _ITEMS_PER_PAGE and return a list of Embeds.
    Each item becomes one inline field: name as the field title, stats as the body.
    Two inline fields sit side-by-side on desktop; they stack vertically on mobile —
    both are readable without horizontal scrolling.
    """
    pages = []

    for page_start in range(0, len(items), _ITEMS_PER_PAGE):
        chunk = items[page_start: page_start + _ITEMS_PER_PAGE]

        embed = nextcord.Embed(
            title=f"🛒  {merchant.name}",
            description=f"*{merchant.description}*",
            color=_EMBED_COLOR,
        )

        for item in chunk:
            embed.add_field(
                name=item.name,
                value=_field_value_for_item(item),
                inline=True,  # side-by-side on desktop, stacked on mobile
            )

        pages.append(embed)

    return pages


def _collect_all_items(
    merchant,
    lookup_inventory_use_case,
    sells_item_types: set,
    sells_item_type_and_filters: dict,
) -> list:
    """
    Fetch all inventory items for a merchant (standard + custom) and return
    them as a flat sorted list of item model objects (not tuples).
    Custom items are appended after DB items so they always appear.
    """
    all_items = []

    type_fetch_map = {
        ItemType.ARMOR: ItemType.ARMOR in sells_item_types,
        ItemType.GENERAL_GOOD: ItemType.GENERAL_GOOD in sells_item_types,
        ItemType.INSTRUMENT: ItemType.INSTRUMENT in sells_item_types,
        ItemType.JEWELRY: ItemType.JEWELRY in sells_item_types,
        ItemType.SONG: ItemType.SONG in sells_item_types,
        ItemType.SPELL: ItemType.SPELL in sells_item_types,
        ItemType.MELEE_WEAPON: ItemType.MELEE_WEAPON in sells_item_types,
        ItemType.RANGED_WEAPON: ItemType.RANGED_WEAPON in sells_item_types,
    }

    for item_type, should_fetch in type_fetch_map.items():
        if not should_fetch:
            continue
        result = lookup_inventory_use_case.lookup_items_by_item_type(
            item_type, sells_item_type_and_filters.get(item_type)
        )
        if result:
            all_items.extend(result)

    # Custom items (already attached to the merchant model)
    if merchant.custom_items:
        all_items.extend(merchant.custom_items)

    # Sort alphabetically by name for consistency
    all_items.sort(key=lambda i: i.name)

    return all_items


# ---------------------------------------------------------------------------
# Use case class
# ---------------------------------------------------------------------------

class BuildInventoryTableUseCase:
    def __init__(self, lookup_city_use_case, lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case):
        self.__lookup_city_use_case = lookup_city_use_case
        self.__lookup_merchant_use_case = lookup_merchant_use_case
        self.__lookup_inventory_use_case = lookup_inventory_use_case
        self.__build_table_use_case = build_table_use_case

    # ------------------------------------------------------------------
    # NEW: Embed-based methods (used by the slash command / mobile UI)
    # ------------------------------------------------------------------

    def build_city_merchants_embed(self, city_name: str) -> nextcord.Embed | None:
        """
        Return a single Embed listing all merchants in a city.
        Returns None if the city is not found.
        """
        city = self.__lookup_city_use_case.lookup_city_by_city_name(city_name)
        if city is None:
            return None

        embed = nextcord.Embed(
            title=f"🏙️  {city.name}",
            color=_EMBED_COLOR,
        )

        if city.directions:
            embed.description = (
                f"*{city.directions.question}*\n\n{city.directions.answer}"
            )

        if city.merchants:
            merchant_lines = "\n".join(
                f"• **{m.name}** — {m.description}" for m in city.merchants
            )
            embed.add_field(name="Merchants", value=merchant_lines, inline=False)
        else:
            embed.add_field(name="Merchants", value="None found.", inline=False)

        return embed

    def build_merchant_inventory_embeds(
        self, city_name: str, merchant_name: str
    ) -> list[nextcord.Embed] | None:
        """
        Return a list of paginated Embeds for a merchant's full inventory.
        Returns None if the merchant is not found.
        """
        merchant = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(
            city_name=city_name, merchant_name=merchant_name
        )
        if merchant is None:
            return None

        sells_item_types = set(
            map(lambda s: s.item_type, merchant.sells_item_types)
        )
        sells_item_type_and_filters = dict(
            map(lambda s: (s.item_type, s.and_filter), merchant.sells_item_types)
        )

        items = _collect_all_items(
            merchant,
            self.__lookup_inventory_use_case,
            sells_item_types,
            sells_item_type_and_filters,
        )

        if not items:
            # Return a single embed saying the inventory is empty
            embed = nextcord.Embed(
                title=f"🛒  {merchant.name}",
                description="This merchant has no items in stock.",
                color=_EMBED_COLOR,
            )
            return [embed]

        return _build_embed_pages(merchant, items)

    # ------------------------------------------------------------------
    # EXISTING: ASCII table method (kept intact — nothing else breaks)
    # ------------------------------------------------------------------

    def build_merchant_inventory_tables(self, city_name, merchant_name):
        merchant = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(city_name=city_name, merchant_name=merchant_name)
        if merchant is not None:
            sells_item_types = set(map(lambda sells_item_type: sells_item_type.item_type, merchant.sells_item_types))
            sells_item_type_and_filters = dict(map(lambda sells_item_type: (sells_item_type.item_type, sells_item_type.and_filter), merchant.sells_item_types))

            has_armor = ItemType.ARMOR in sells_item_types
            has_general_good = ItemType.GENERAL_GOOD in sells_item_types
            has_instrument = ItemType.INSTRUMENT in sells_item_types
            has_jewelry = ItemType.JEWELRY in sells_item_types
            has_song = ItemType.SONG in sells_item_types
            has_spell = ItemType.SPELL in sells_item_types
            has_melee_weapon = ItemType.MELEE_WEAPON in sells_item_types
            has_ranged_weapon = ItemType.RANGED_WEAPON in sells_item_types

            custom_item_types = set(map(lambda custom_item: custom_item.item_type, merchant.custom_items))

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
                merchant.custom_items,
                armor=display_armor_columns,
                instruments=display_instrument_columns,
                songs=display_songs_columns,
                spells=display_spell_columns,
                weapons=display_weapon_columns,
                misc_items=has_custom_misc_item
            ) if merchant.custom_items else ()

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

            max_rows = merchant.number_of_table_rows

            inventory_tables = self.__build_table_use_case.build_ascii_tables(headers, rows, max_rows=max_rows)
            if len(inventory_tables) == 1:
                return [f"```{merchant.name}'s Inventory:\n{inventory_tables[0]}```"]
            else:
                tables = []
                for index, chunk in enumerate(inventory_tables):
                    tables.append(f"```{merchant.name}'s Inventory (Part {index + 1} / {len(inventory_tables)}):\n{inventory_tables[index]}```")
                return tables

        else:
            return None
