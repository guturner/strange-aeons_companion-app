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
# Embed helpers
# ---------------------------------------------------------------------------

_EMBED_COLOR = 0xC8A96E  # Parchment gold

_ITEMS_PER_PAGE = 6  # Full-width fields are taller, so 6 is a comfortable page


# ------------------------------------------------------------------
# Icon maps
# ------------------------------------------------------------------

# Icon shown in the embed title based on merchant description
_MERCHANT_ICON: dict[str, str] = {
    "armorer":      "🛡️",
    "blacksmith":   "⚒️",
    "bowyer":       "🏹",
    "general goods":"🎒",
    "jeweler":      "💎",
    "songs":        "🎵",
    "spells":       "📜",
    "instruments":  "🪗",
}

# Icon prefixed to the item name line based on ItemType
_ITEM_TYPE_ICON: dict[ItemType, str] = {
    ItemType.ARMOR:        "🛡️",
    ItemType.MELEE_WEAPON: "⚔️",
    ItemType.RANGED_WEAPON:"🏹",
    ItemType.JEWELRY:      "💍",
    ItemType.GENERAL_GOOD: "🎒",
    ItemType.SONG:         "🎵",
    ItemType.SPELL:        "📜",
    ItemType.INSTRUMENT:   "🎶",
}


def _merchant_icon(description: str) -> str:
    return _MERCHANT_ICON.get(description.lower().strip(), "🏪")


def _item_icon(item_type: ItemType) -> str:
    return _ITEM_TYPE_ICON.get(item_type, "📦")


# ------------------------------------------------------------------
# Field value builder
# ------------------------------------------------------------------

def _skip(val) -> bool:
    return not val or str(val).strip() in ("", "--", "—", "None")


def _field_value_for_item(item) -> str:
    """
    Renders one item as a richly formatted full-width embed field value.

    Layout:
        🏹  **Runed Oak Bow**
        `Medium, Martial`  ·  ⚔️ 1D6 +2  ·  🎯 19-20, x3  ·  ⏱️ Standard
        Composite Shortbow; Atk +2; Keen
        ─────────────────────────────
        💰 **15,630 GP**

    The separator line (─────) visually closes each card without needing
    Discord features that don't exist (background color, borders).
    """
    icon = _item_icon(item.item_type)
    lines = []

    # ── Item name (bold, with type icon) ──────────────────────────
    lines.append(f"{icon}  **{item.name}**")

    # ── Compact stat line ─────────────────────────────────────────
    stat_chips = []

    if not _skip(item.size):
        stat_chips.append(f"`{item.size}`")

    # Armor stats
    if not _skip(item.armor_bonus):
        stat_chips.append(f"AC {item.armor_bonus}")
    if not _skip(item.max_dexterity):
        stat_chips.append(f"Dex {item.max_dexterity}")
    if not _skip(item.armor_check_penalty):
        stat_chips.append(f"ACP {item.armor_check_penalty}")

    # Weapon stats
    if not _skip(item.damage):
        stat_chips.append(f"⚔️ {item.damage}")
    if not _skip(item.crit_range):
        stat_chips.append(f"🎯 {item.crit_range}")
    if not _skip(item.delay):
        stat_chips.append(f"⏱️ {item.delay}")

    # Song / spell
    if hasattr(item, "song_instrument") and not _skip(item.song_instrument):
        stat_chips.append(f"{item.song_instrument}")
    if hasattr(item, "spell_level") and not _skip(item.spell_level):
        stat_chips.append(f"Lvl {item.spell_level}")

    if stat_chips:
        lines.append("  ·  ".join(stat_chips))

    # ── Description / spell description ───────────────────────────
    if hasattr(item, "spell_description") and not _skip(item.spell_description):
        lines.append(f"*{item.spell_description}*")

    # ── Stats (free-text flavour line) ────────────────────────────
    if not _skip(item.stats):
        lines.append(f"Unique Stats: _{item.stats}_")

    # ── Separator + price ─────────────────────────────────────────
    lines.append("┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")
    if not _skip(item.cost):
        lines.append(f"💰 **{item.cost}**")
    else:
        lines.append("💰 *Price unknown*")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Page builder
# ------------------------------------------------------------------

def _build_embed_pages(merchant, items: list) -> list[nextcord.Embed]:
    """
    One full-width field per item. Full-width (inline=False) fields stack
    vertically on both desktop and mobile — no awkward side-by-side layout
    that collapses oddly on narrow screens.
    """
    icon = _merchant_icon(merchant.description)
    pages = []

    for page_start in range(0, len(items), _ITEMS_PER_PAGE):
        chunk = items[page_start: page_start + _ITEMS_PER_PAGE]

        embed = nextcord.Embed(
            title=f"{icon}  {merchant.name}",
            description=f"-# {merchant.description}",
            color=_EMBED_COLOR,
        )

        for item in chunk:
            embed.add_field(
                name="",           # empty name — the item name lives in the value
                value=_field_value_for_item(item),
                inline=False,      # full-width: readable on any screen size
            )

        pages.append(embed)

    return pages


# ------------------------------------------------------------------
# Item collector (unchanged logic, extracted for clarity)
# ------------------------------------------------------------------

def _collect_all_items(
    merchant,
    lookup_inventory_use_case,
    sells_item_types: set,
    sells_item_type_and_filters: dict,
) -> list:
    all_items = []

    type_fetch_map = {
        ItemType.ARMOR:        ItemType.ARMOR in sells_item_types,
        ItemType.GENERAL_GOOD: ItemType.GENERAL_GOOD in sells_item_types,
        ItemType.INSTRUMENT:   ItemType.INSTRUMENT in sells_item_types,
        ItemType.JEWELRY:      ItemType.JEWELRY in sells_item_types,
        ItemType.SONG:         ItemType.SONG in sells_item_types,
        ItemType.SPELL:        ItemType.SPELL in sells_item_types,
        ItemType.MELEE_WEAPON: ItemType.MELEE_WEAPON in sells_item_types,
        ItemType.RANGED_WEAPON:ItemType.RANGED_WEAPON in sells_item_types,
    }

    for item_type, should_fetch in type_fetch_map.items():
        if not should_fetch:
            continue
        result = lookup_inventory_use_case.lookup_items_by_item_type(
            item_type, sells_item_type_and_filters.get(item_type)
        )
        if result:
            all_items.extend(result)

    if merchant.custom_items:
        all_items.extend(merchant.custom_items)

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
    # Embed methods (slash command / mobile UI)
    # ------------------------------------------------------------------

    def build_city_merchants_embed(self, city_name: str) -> nextcord.Embed | None:
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
                f"{_merchant_icon(m.description)}  **{m.name}** — *{m.description}*"
                for m in city.merchants
            )
            embed.add_field(name="Merchants", value=merchant_lines, inline=False)
        else:
            embed.add_field(name="Merchants", value="None found.", inline=False)

        return embed

    def build_merchant_inventory_embeds(
        self, city_name: str, merchant_name: str
    ) -> list[nextcord.Embed] | None:
        merchant = self.__lookup_merchant_use_case.lookup_merchant_by_city_name_and_merchant_name(
            city_name=city_name, merchant_name=merchant_name
        )
        if merchant is None:
            return None

        sells_item_types = set(map(lambda s: s.item_type, merchant.sells_item_types))
        sells_item_type_and_filters = dict(map(lambda s: (s.item_type, s.and_filter), merchant.sells_item_types))

        items = _collect_all_items(
            merchant,
            self.__lookup_inventory_use_case,
            sells_item_types,
            sells_item_type_and_filters,
        )

        if not items:
            icon = _merchant_icon(merchant.description)
            embed = nextcord.Embed(
                title=f"{icon}  {merchant.name}",
                description="This merchant has no items in stock.",
                color=_EMBED_COLOR,
            )
            return [embed]

        return _build_embed_pages(merchant, items)

    def lookup_city_by_name(self, city_name: str):
        return self.__lookup_city_use_case.lookup_city_by_city_name(city_name)

    def lookup_cities_by_discord_user_id(self, discord_user_id: int):
        return self.__lookup_city_use_case.lookup_cities_by_discord_user_id(discord_user_id)

    # ------------------------------------------------------------------
    # ASCII table method (kept intact)
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

            armor_inventory_data = _get_inventory_data(has_armor, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.ARMOR, sells_item_type_and_filters[ItemType.ARMOR]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            general_goods_inventory_data = _get_inventory_data(has_general_good, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.GENERAL_GOOD, sells_item_type_and_filters[ItemType.GENERAL_GOOD]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            instruments_inventory_data = _get_inventory_data(has_instrument, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.INSTRUMENT, sells_item_type_and_filters[ItemType.INSTRUMENT]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            jewelry_inventory_data = _get_inventory_data(has_jewelry, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.JEWELRY, sells_item_type_and_filters[ItemType.JEWELRY]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            songs_inventory_data = _get_inventory_data(has_song, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.SONG, sells_item_type_and_filters[ItemType.SONG]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            spells_inventory_data = _get_inventory_data(has_spell, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.SPELL, sells_item_type_and_filters[ItemType.SPELL]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            melee_weapons_inventory_data = _get_inventory_data(has_melee_weapon, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.MELEE_WEAPON, sells_item_type_and_filters[ItemType.MELEE_WEAPON]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)
            ranged_weapons_inventory_data = _get_inventory_data(has_ranged_weapon, lambda: self.__lookup_inventory_use_case.lookup_items_by_item_type(ItemType.RANGED_WEAPON, sells_item_type_and_filters[ItemType.RANGED_WEAPON]), armor=display_armor_columns, instruments=display_instrument_columns, songs=display_songs_columns, spells=display_spell_columns, weapons=display_weapon_columns, misc_items=has_custom_misc_item)

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