import unittest
from unittest.mock import AsyncMock, MagicMock, Mock

import nextcord

from cogs.shop_cog import ShopCog
from models.item import ItemType, SellsItemType
from tests.utils import (
    city, item_armor_jewelry, item_custom_armor,
    item_general_good, item_general_jewelry, item_instrument, item_melee_weapon,
    item_misc, item_song, item_spell, merchant, mock_get_city_by_city_name, recipe_book,
)
from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupItemsUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_interaction(user_id: int = 1, username: str = "fake_username_1") -> MagicMock:
    interaction = MagicMock(spec=nextcord.Interaction)
    interaction.user = MagicMock()
    interaction.user.id = user_id
    interaction.user.name = username
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


def _make_stack(mock_city_dao=None, mock_item_dao=None):
    """
    Builds a fully wired use-case stack for integration tests.
    Callers supply mock DAOs; everything else is real.
    """
    if mock_city_dao is None:
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

    lookup_city_use_case = LookupCityUseCase(mock_city_dao)
    lookup_inventory_use_case = LookupItemsUseCase(mock_item_dao) if mock_item_dao else LookupItemsUseCase(Mock())
    lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
    build_inventory_table_use_case = BuildInventoryTableUseCase(
        lookup_merchant_use_case, lookup_inventory_use_case,
    )
    rb = recipe_book(
        lookup_city_use_case=lookup_city_use_case,
        lookup_inventory_use_case=lookup_inventory_use_case,
        lookup_merchant_use_case=lookup_merchant_use_case,
        build_inventory_table_use_case=build_inventory_table_use_case,
    )
    bot = MagicMock()
    return ShopCog(bot, rb)


def _send_kwargs(interaction: MagicMock) -> dict:
    return interaction.followup.send.call_args.kwargs


# ---------------------------------------------------------------------------
# BuildInventoryTableUseCase — unit tests (no Discord)
# ---------------------------------------------------------------------------

class TestBuildInventoryTableUseCase(unittest.TestCase):

    def _make_use_case(self, mock_city_dao=None, mock_item_dao=None):
        if mock_city_dao is None:
            mock_city_dao = Mock()
            mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        lookup_inventory_use_case = LookupItemsUseCase(mock_item_dao or Mock())
        return (
            BuildInventoryTableUseCase(
                lookup_merchant_use_case, lookup_inventory_use_case,
            ),
            lookup_city_use_case,
        )

    def test_build_city_merchants_embed__returns_embed(self):
        uc, lookup_city = self._make_use_case()
        embed = uc.build_city_merchants_embed("Qeynos", lookup_city)
        assert embed is not None
        assert isinstance(embed, nextcord.Embed)

    def test_build_city_merchants_embed__city_name_in_title(self):
        uc, lookup_city = self._make_use_case()
        embed = uc.build_city_merchants_embed("Qeynos", lookup_city)
        assert "Qeynos" in embed.title

    def test_build_city_merchants_embed__merchant_names_in_fields(self):
        uc, lookup_city = self._make_use_case()
        embed = uc.build_city_merchants_embed("Qeynos", lookup_city)
        field_values = " ".join(f.value for f in embed.fields)
        assert "Mr. Chant" in field_values
        assert "Ensign Chant" in field_values

    def test_build_city_merchants_embed__city_not_found_returns_none(self):
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = None
        uc, lookup_city = self._make_use_case(mock_city_dao=mock_city_dao)
        result = uc.build_city_merchants_embed("Fakesville", lookup_city)
        assert result is None

    def test_build_merchant_inventory_embeds__returns_pages(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        uc, _ = self._make_use_case(mock_item_dao=mock_item_dao)
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Mr. Chant")
        assert pages is not None
        assert len(pages) >= 1

    def test_build_merchant_inventory_embeds__item_name_in_field(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        uc, _ = self._make_use_case(mock_item_dao=mock_item_dao)
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Mr. Chant")
        all_field_text = " ".join(f.value for p in pages for f in p.fields)
        assert "Widget" in all_field_text

    def test_build_merchant_inventory_embeds__merchant_not_found_returns_none(self):
        uc, _ = self._make_use_case()
        result = uc.build_merchant_inventory_embeds("Qeynos", "Nobody Here")
        assert result is None

    def test_build_merchant_inventory_embeds__empty_stock_returns_embed(self):
        # Merchant exists but has no items
        mock_city_dao = Mock()
        empty_merchant = merchant(name="Empty Ned", sells_item_types=[])
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[empty_merchant], occupants=[1]
        )
        uc, _ = self._make_use_case(mock_city_dao=mock_city_dao)
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Empty Ned")
        assert pages is not None and len(pages) == 1
        assert "no items" in pages[0].description.lower()

    def test_build_merchant_inventory_embeds__pagination(self):
        # 7 items across a 6-per-page limit → 2 pages.
        # Use a jewelry-only merchant so only one item-type fetch fires,
        # giving us exactly 7 items regardless of how many types the mock returns.
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_jewelry()] * 7
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos",
            merchants=[merchant(name="Ensign Chant", description="Jeweler",
                                sells_item_types=[SellsItemType("jewelry", None)])],
            occupants=[1],
        )
        uc, _ = self._make_use_case(mock_city_dao=mock_city_dao, mock_item_dao=mock_item_dao)
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Ensign Chant")
        assert len(pages) == 2

    # ── Item type rendering smoke tests ────────────────────────────────────

    def _render_fields(self, items, merch=None):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = items
        if merch is None:
            merch = merchant(name="Mr. Chant", sells_item_types=[SellsItemType("general_good", None)])
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[merch], occupants=[1]
        )
        uc, _ = self._make_use_case(mock_city_dao=mock_city_dao, mock_item_dao=mock_item_dao)
        pages = uc.build_merchant_inventory_embeds("Qeynos", merch.name)
        return " ".join(f.value for p in pages for f in p.fields)

    def test_item_rendering__melee_weapon__shows_damage(self):
        text = self._render_fields([item_melee_weapon()])
        assert "1D10" in text

    def test_item_rendering__armor__shows_ac(self):
        merch = merchant(name="Mr. Chant", sells_item_types=[SellsItemType("armor", None)])
        text = self._render_fields([item_custom_armor()], merch=merch)
        assert "+10" in text   # armor_bonus

    def test_item_rendering__jewelry__shows_name(self):
        text = self._render_fields([item_general_jewelry()])
        assert "Star Sapphire" in text

    def test_item_rendering__song__shows_instrument(self):
        merch = merchant(name="Song Mann", description="Songs", sells_item_types=[SellsItemType("song", None)])
        text = self._render_fields([item_song()], merch=merch)
        assert "String" in text

    def test_item_rendering__spell__shows_description(self):
        merch = merchant(name="Spell Mann", description="Spells", sells_item_types=[SellsItemType("spell", None)])
        text = self._render_fields([item_spell()], merch=merch)
        assert "9000" in text

    def test_item_rendering__instrument__shows_name(self):
        merch = merchant(name="Miss C", custom_items=[item_instrument()])
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[merch], occupants=[1]
        )
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        uc = BuildInventoryTableUseCase(lookup_merchant_use_case, LookupItemsUseCase(Mock()))
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Miss C")
        text = " ".join(f.value for p in pages for f in p.fields)
        assert "Lucille" in text

    def test_item_rendering__misc__shows_name(self):
        merch = merchant(name="Miss C", custom_items=[item_misc()])
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[merch], occupants=[1]
        )
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        uc = BuildInventoryTableUseCase(lookup_merchant_use_case, LookupItemsUseCase(Mock()))
        pages = uc.build_merchant_inventory_embeds("Qeynos", "Miss C")
        text = " ".join(f.value for p in pages for f in p.fields)
        assert "Doohickey" in text


# ---------------------------------------------------------------------------
# ShopCog._shop_impl — integration tests (real use-case stack, mocked Discord)
# ---------------------------------------------------------------------------

class TestShopCog(unittest.IsolatedAsyncioTestCase):

    async def test_shop__list_merchants__happy_path(self):
        """No merchant name → city embed with merchant listing."""
        shop_cog = _make_stack()
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos")

        interaction.response.defer.assert_called_once_with(ephemeral=True)
        interaction.followup.send.assert_called_once()
        kwargs = _send_kwargs(interaction)
        assert kwargs.get("ephemeral") is True
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Qeynos" in embed.title

    async def test_shop__list_merchants__merchant_names_in_embed(self):
        shop_cog = _make_stack()
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Mr. Chant" in field_text
        assert "Ensign Chant" in field_text

    async def test_shop__inventory__happy_path(self):
        """Merchant name supplied → inventory embed."""
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Mr. Chant")

        interaction.response.defer.assert_called_once_with(ephemeral=True)
        interaction.followup.send.assert_called_once()
        kwargs = _send_kwargs(interaction)
        assert kwargs.get("ephemeral") is True
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Mr. Chant" in embed.title

    async def test_shop__inventory__item_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Mr. Chant")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Widget" in field_text

    async def test_shop__inventory__weapon_stats_in_embed(self):
        mock_item_dao = Mock()
        def by_type(item_type, _filter):
            if item_type == ItemType.MELEE_WEAPON:
                return [item_melee_weapon()]
            return []
        mock_item_dao.get_items_by_item_type.side_effect = by_type
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Mr. Chant")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Wabbajack" in field_text
        assert "1D10" in field_text

    async def test_shop__inventory__jewelry_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_armor_jewelry(), item_general_jewelry()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Ensign Chant")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Star Sapphire" in field_text
        assert "Khaji Da" in field_text

    async def test_shop__inventory__custom_armor_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Custom Or")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Customizer I" in field_text

    async def test_shop__inventory__custom_weapon_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_general_good()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Custom On")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Customizer II" in field_text

    async def test_shop__inventory__songs_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_song()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Song Mann")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Kumbaya" in field_text

    async def test_shop__inventory__spells_in_embed(self):
        mock_item_dao = Mock()
        mock_item_dao.get_items_by_item_type.return_value = [item_spell()]
        shop_cog = _make_stack(mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Spell Mann")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Kamehameha" in field_text

    async def test_shop__inventory__instruments_in_embed(self):
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[merchant(name="Miss C", custom_items=[item_instrument()])], occupants=[1]
        )
        shop_cog = _make_stack(mock_city_dao=mock_city_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Miss C")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Lucille" in field_text

    async def test_shop__inventory__misc_only_in_embed(self):
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos", merchants=[merchant(name="Miss C", custom_items=[item_misc()])], occupants=[1]
        )
        shop_cog = _make_stack(mock_city_dao=mock_city_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Miss C")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Doohickey" in field_text

    async def test_shop__inventory__misc_and_general_goods_in_embed(self):
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = city(
            "Qeynos",
            merchants=[merchant(name="Miss C", sells_item_types=[SellsItemType("general_good", None)], custom_items=[item_misc()])],
            occupants=[1]
        )
        mock_item_dao = Mock()
        def by_type(item_type, _filter):
            if item_type == ItemType.GENERAL_GOOD:
                return [item_general_good()]
            return []
        mock_item_dao.get_items_by_item_type.side_effect = by_type
        shop_cog = _make_stack(mock_city_dao=mock_city_dao, mock_item_dao=mock_item_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Miss C")

        embed = _send_kwargs(interaction).get("embed")
        field_text = " ".join(f.value for f in embed.fields)
        assert "Doohickey" in field_text
        assert "Widget" in field_text

    async def test_shop__invalid_city__returns_error(self):
        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.return_value = None
        shop_cog = _make_stack(mock_city_dao=mock_city_dao)
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Fakesville", merchant_name="Mr. Chant")

        kwargs = _send_kwargs(interaction)
        assert kwargs.get("embed") is None
        text = interaction.followup.send.call_args.args[0]
        assert "Fakesville" in text

    async def test_shop__merchant_not_found__returns_error(self):
        shop_cog = _make_stack()
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos", merchant_name="Nobody Here")

        kwargs = _send_kwargs(interaction)
        assert kwargs.get("embed") is None
        text = interaction.followup.send.call_args.args[0]
        assert "Nobody Here" in text

    async def test_shop__defers_ephemeral(self):
        shop_cog = _make_stack()
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos")

        interaction.response.defer.assert_called_once_with(ephemeral=True)

    async def test_shop__response_is_ephemeral(self):
        shop_cog = _make_stack()
        interaction = _make_interaction()

        await ShopCog._shop_impl(shop_cog, interaction, city_name="Qeynos")

        assert _send_kwargs(interaction).get("ephemeral") is True