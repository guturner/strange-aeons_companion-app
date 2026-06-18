import nextcord

from models.item import ItemType

_EMBED_COLOR = 0xC8A96E
_ITEMS_PER_PAGE = 6


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


# ---------------------------------------------------------------------------
# Item field builder
# ---------------------------------------------------------------------------

def _skip(val) -> bool:
    return not val or str(val).strip() in ("", "--", "—", "None")


def _field_value_for_item(item) -> str:
    """
    Renders one item as a richly formatted full-width embed field value.

    Layout:
        🏹  **Runed Oak Bow**
        `Medium, Martial`  ·  ⚔️ 1D6 +2  ·  🎯 19-20, x3  ·  ⏱️ Standard
        Unique Stats: Composite Shortbow; Atk +2; Keen
        ─────────────────────────────
        💰 **15,630 GP**
    """
    icon = _item_icon(item.item_type)
    lines = []

    lines.append(f"{icon}  **{item.name}**")

    stat_chips = []

    if not _skip(item.size):
        stat_chips.append(f"`{item.size}`")

    if not _skip(item.armor_bonus):
        stat_chips.append(f"AC {item.armor_bonus}")
    if not _skip(item.max_dexterity):
        stat_chips.append(f"Dex {item.max_dexterity}")
    if not _skip(item.armor_check_penalty):
        stat_chips.append(f"ACP {item.armor_check_penalty}")

    if not _skip(item.damage):
        stat_chips.append(f"⚔️ {item.damage}")
    if not _skip(item.crit_range):
        stat_chips.append(f"🎯 {item.crit_range}")
    if not _skip(item.delay):
        stat_chips.append(f"⏱️ {item.delay}")

    if hasattr(item, "song_instrument") and not _skip(item.song_instrument):
        stat_chips.append(f"{item.song_instrument}")
    if hasattr(item, "spell_level") and not _skip(item.spell_level):
        stat_chips.append(f"Lvl {item.spell_level}")

    if stat_chips:
        lines.append("  ·  ".join(stat_chips))

    if hasattr(item, "spell_description") and not _skip(item.spell_description):
        lines.append(f"*{item.spell_description}*")

    if not _skip(item.stats):
        lines.append(f"Unique Stats: _{item.stats}_")

    lines.append("┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")
    if not _skip(item.cost):
        lines.append(f"💰 **{item.cost}**")
    else:
        lines.append("💰 *Price unknown*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def _build_embed_pages(merchant, items: list) -> list[nextcord.Embed]:
    """One full-width field per item, stacking vertically on desktop and mobile."""
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
                name="",
                value=_field_value_for_item(item),
                inline=False,
            )

        pages.append(embed)

    return pages


def _build_city_embed(city) -> nextcord.Embed:
    """Builds the merchant-listing embed for a city."""
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


# ---------------------------------------------------------------------------
# Item collector
# ---------------------------------------------------------------------------

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
    """
    Builds Discord embeds for the /shop slash command.

    City-level lookups (autocomplete, occupant check) belong to the cog layer
    via LookupCityUseCase directly, not here.
    """

    def __init__(self, lookup_merchant_use_case, lookup_inventory_use_case):
        self.__lookup_merchant_use_case = lookup_merchant_use_case
        self.__lookup_inventory_use_case = lookup_inventory_use_case

    def build_city_merchants_embed(self, city_name: str, lookup_city_use_case) -> nextcord.Embed | None:
        """
        Returns a city-merchants listing embed, or None if the city is not found.

        :param city_name: Name of the city to look up.
        :param lookup_city_use_case: Injected at call site (cog layer) so this
            class does not need to hold a city DAO reference.
        """
        city = lookup_city_use_case.lookup_city_by_city_name(city_name)
        if city is None:
            return None
        return _build_city_embed(city)

    def build_merchant_inventory_embeds(
        self, city_name: str, merchant_name: str
    ) -> list[nextcord.Embed] | None:
        """
        Returns paginated inventory embeds for a specific merchant, or None if
        the merchant is not found in the city.
        """
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