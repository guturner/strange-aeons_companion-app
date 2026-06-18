from testcontainers.mongodb import MongoDbContainer
from unittest.mock import AsyncMock, MagicMock

import nextcord

from cogs.shop_cog import ShopCog
from daos.city_dao import CityDAO
from daos.item_dao import ItemDAO
from models.database import Database
from tests.e2e_test import E2ETest
from tests.utils import recipe_book
from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupItemsUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_interaction() -> MagicMock:
    interaction = MagicMock(spec=nextcord.Interaction)
    interaction.user = MagicMock()
    interaction.user.id = 2
    interaction.user.name = "a_player_1"
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


def _make_shop_cog(uri: str, db_name: str) -> ShopCog:
    """Builds a fully wired ShopCog against the live test database."""
    db = Database(uri, db_name)
    lookup_city_use_case      = LookupCityUseCase(CityDAO(db))
    lookup_inventory_use_case = LookupItemsUseCase(ItemDAO(db))
    lookup_merchant_use_case  = LookupMerchantUseCase(lookup_city_use_case)
    build_inventory_table_use_case = BuildInventoryTableUseCase(
        lookup_merchant_use_case, lookup_inventory_use_case
    )
    rb = recipe_book(
        lookup_city_use_case=lookup_city_use_case,
        lookup_inventory_use_case=lookup_inventory_use_case,
        lookup_merchant_use_case=lookup_merchant_use_case,
        build_inventory_table_use_case=build_inventory_table_use_case,
    )
    return ShopCog(MagicMock(), rb)


def _all_pages_field_text(shop_cog: ShopCog, city_name: str, merchant_name: str) -> str:
    """
    Fetches all embed pages for a merchant directly from the use case and
    returns all field values as a single string.

    This sidesteps the PaginatedView button flow — only the first page arrives
    via followup.send; subsequent pages are delivered when users click Next,
    which we don't simulate in tests.
    """
    pages = shop_cog.recipe_book.build_inventory_table.build_merchant_inventory_embeds(
        city_name, merchant_name
    )
    return " ".join(f.value for page in pages for f in page.fields)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestShopCogE2E(E2ETest):

    async def __setup_environment(self, mongo):
        self.load_cities_data(mongo)
        self.load_items_data(mongo)
        self.load_users_data(mongo)

    # ── General goods ───────────────────────────────────────────────────────

    async def test_shop__general_goods__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            interaction = _make_interaction()

            await ShopCog._shop_impl(
                shop_cog, interaction,
                city_name="Ak'Anon",
                merchant_name="Clockwork Merchant XXIII",
            )

            first_embed = interaction.followup.send.call_args_list[0].kwargs["embed"]
            assert "Clockwork Merchant XXIII" in first_embed.title

            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Merchant XXIII")
            for item_name in ["Bedroll", "Bell", "Candle", "Crowbar", "Flask",
                               "Mirror", "Rope, Hemp (50 ft.)", "Spade", "Torch", "Water Skin"]:
                assert item_name in all_text, f"Expected '{item_name}' in general goods inventory"

    async def test_shop__general_goods__correct_page_count(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            pages = shop_cog.recipe_book.build_inventory_table.build_merchant_inventory_embeds(
                "Ak'Anon", "Clockwork Merchant XXIII"
            )

            assert len(pages) == 6

    # ── Weapons & armour ────────────────────────────────────────────────────

    async def test_shop__weapons__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            interaction = _make_interaction()

            await ShopCog._shop_impl(
                shop_cog, interaction,
                city_name="Ak'Anon",
                merchant_name="Clockwork Blacksmith II",
            )

            first_embed = interaction.followup.send.call_args_list[0].kwargs["embed"]
            assert "Clockwork Blacksmith II" in first_embed.title

            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Blacksmith II")
            for item_name in ["Axe, Throwing", "Battleaxe", "Broad Sword", "Dagger",
                               "Greatsword", "Handaxe", "Warhammer", "Two-Handed Hammer",
                               "Banded Mail", "Full Plate", "Half-Plate", "Splint Mail"]:
                assert item_name in all_text, f"Expected '{item_name}' in blacksmith inventory"

    async def test_shop__weapons__damage_shown_in_embed(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Blacksmith II")
            assert "1D8" in all_text or "2D6" in all_text

    async def test_shop__weapons__armor_bonus_shown_in_embed(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Blacksmith II")
            assert "AC +" in all_text

    # ── Spells ──────────────────────────────────────────────────────────────

    async def test_shop__spells__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            interaction = _make_interaction()

            await ShopCog._shop_impl(
                shop_cog, interaction,
                city_name="Ak'Anon",
                merchant_name="Clockwork Merchant XVI",
            )

            first_embed = interaction.followup.send.call_args_list[0].kwargs["embed"]
            assert "Clockwork Merchant XVI" in first_embed.title

            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Merchant XVI")
            for item_name in ["Burn", "Cure Disease", "Cure Poison", "Disease Cloud",
                               "Elementaling: Air", "Flame Bolt", "Invisibility",
                               "Minor Healing", "Minor Shielding", "Shock of Blades",
                               "Staff of Tracing"]:
                assert item_name in all_text, f"Expected spell '{item_name}' in spell merchant inventory"

    async def test_shop__spells__description_shown_in_embed(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Merchant XVI")
            assert "1D10 fire dmg" in all_text

    async def test_shop__spells__level_shown_in_embed(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            all_text = _all_pages_field_text(shop_cog, "Ak'Anon", "Clockwork Merchant XVI")
            assert "Lvl Mag" in all_text

    # ── Interaction / response shape ────────────────────────────────────────

    async def test_shop__defers_ephemeral(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            interaction = _make_interaction()

            await ShopCog._shop_impl(
                shop_cog, interaction,
                city_name="Ak'Anon",
                merchant_name="Clockwork Merchant XXIII",
            )

            interaction.response.defer.assert_called_once_with(ephemeral=True)

    async def test_shop__response_is_ephemeral(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            await self.__setup_environment(mongo)
            mongo_client = mongo.get_connection_client()
            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            shop_cog = _make_shop_cog(mongo.get_connection_url(), "everquest")
            interaction = _make_interaction()

            await ShopCog._shop_impl(
                shop_cog, interaction,
                city_name="Ak'Anon",
                merchant_name="Clockwork Merchant XXIII",
            )

            first_call_kwargs = interaction.followup.send.call_args_list[0].kwargs
            assert first_call_kwargs.get("ephemeral") is True