import unittest

from unittest.mock import AsyncMock, MagicMock, Mock

from cogs.shop_cog import ShopCog
from models.city import InventoryType
from tests.utils import mock_get_general_goods, mock_get_jewelry, mock_get_weapons, mock_get_city_by_city_name, recipe_book, city, merchant

from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.build_table_use_case import BuildTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupInventoryUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase


class TestShopCog(unittest.IsolatedAsyncioTestCase):
    async def test_shop__general_goods_and_weapons__happy_path(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        mock_inventory_dao = Mock()
        mock_inventory_dao.get_general_goods.side_effect = mock_get_general_goods
        mock_inventory_dao.get_weapons.side_effect = mock_get_weapons

        build_table_use_case = BuildTableUseCase()
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_inventory_use_case = LookupInventoryUseCase(mock_inventory_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

        shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case, lookup_city_use_case=lookup_city_use_case, lookup_inventory_use_case=lookup_inventory_use_case, lookup_merchant_use_case=lookup_merchant_use_case, build_inventory_table_use_case=build_inventory_table_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos", "Mr.", "Chant")

        # Then
        ctx.send.assert_called_once_with("```Mr. Chant's Inventory:\n+-----------+--------------+----------+------+------------+-------+----------------+----------------------+\n| NAME      | TYPE         | COST     | DMG  | CRIT       | DELAY | SIZE           | STATS                |\n+-----------+--------------+----------+------+------------+-------+----------------+----------------------+\n| Wabbajack | Weapon       | 10000 GP | 1D10 | 10-20, x10 | Quick | Large, Martial | magic resistance (5) |\n| Widget    | General Good | 100 GP   | --   | --         | --    | --             | --                   |\n+-----------+--------------+----------+------+------------+-------+----------------+----------------------+```")

    async def test_shop__jewelry__happy_path(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        mock_inventory_dao = Mock()
        mock_inventory_dao.get_jewelry.side_effect = mock_get_jewelry

        build_table_use_case = BuildTableUseCase()
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_inventory_use_case = LookupInventoryUseCase(mock_inventory_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

        shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case, lookup_city_use_case=lookup_city_use_case, lookup_inventory_use_case=lookup_inventory_use_case, lookup_merchant_use_case=lookup_merchant_use_case, build_inventory_table_use_case=build_inventory_table_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos", "Ensign", "Chant")

        # Then
        ctx.send.assert_called_once_with("```Ensign Chant's Inventory:\n+---------------+---------+-----------+\n| NAME          | TYPE    | COST      |\n+---------------+---------+-----------+\n| Khaji Da      | Jewelry | 100000 GP |\n| Star Sapphire | Jewelry | 1000 GP   |\n+---------------+---------+-----------+```")

    async def test_shop__general_goods_and_custom_armor__happy_path(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        mock_inventory_dao = Mock()
        mock_inventory_dao.get_general_goods.side_effect = mock_get_general_goods

        build_table_use_case = BuildTableUseCase()
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_inventory_use_case = LookupInventoryUseCase(mock_inventory_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

        shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case, lookup_city_use_case=lookup_city_use_case, lookup_inventory_use_case=lookup_inventory_use_case, lookup_merchant_use_case=lookup_merchant_use_case, build_inventory_table_use_case=build_inventory_table_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos", "Custom", "Or")

        # Then
        ctx.send.assert_called_once_with("```Custom Or's Inventory:\n+--------------+--------------+---------+-----+---------+-----+-------+----------------------+\n| NAME         | TYPE         | COST    | AC  | MAX DEX | ACP | SIZE  | STATS                |\n+--------------+--------------+---------+-----+---------+-----+-------+----------------------+\n| Customizer I | Armor        | 1000 GP | +10 | +5      | -2  | Heavy | magic resistance (5) |\n| Widget       | General Good | 100 GP  | --  | --      | --  | --    | --                   |\n+--------------+--------------+---------+-----+---------+-----+-------+----------------------+```")

    async def test_shop__general_goods_and_custom_weapon__happy_path(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        mock_inventory_dao = Mock()
        mock_inventory_dao.get_general_goods.side_effect = mock_get_general_goods

        build_table_use_case = BuildTableUseCase()
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_inventory_use_case = LookupInventoryUseCase(mock_inventory_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

        shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case, lookup_city_use_case=lookup_city_use_case, lookup_inventory_use_case=lookup_inventory_use_case, lookup_merchant_use_case=lookup_merchant_use_case, build_inventory_table_use_case=build_inventory_table_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos", "Custom", "On")

        # Then
        ctx.send.assert_called_once_with("```Custom On's Inventory:\n+---------------+--------------+---------+------+------------+-------+----------------+----------------------+\n| NAME          | TYPE         | COST    | DMG  | CRIT       | DELAY | SIZE           | STATS                |\n+---------------+--------------+---------+------+------------+-------+----------------+----------------------+\n| Customizer II | Weapon       | 1000 GP | 1D10 | 10-20, x10 | Quick | Large, Martial | magic resistance (5) |\n| Widget        | General Good | 100 GP  | --   | --         | --    | --             | --                   |\n+---------------+--------------+---------+------+------------+-------+----------------+----------------------+```")

    async def test_shop__lookup_merchants__happy_path(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        mock_inventory_dao = Mock()

        build_table_use_case = BuildTableUseCase()
        lookup_city_use_case = LookupCityUseCase(mock_city_dao)
        lookup_inventory_use_case = LookupInventoryUseCase(mock_inventory_dao)
        lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
        build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

        shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case,
                                            lookup_city_use_case=lookup_city_use_case,
                                            lookup_inventory_use_case=lookup_inventory_use_case,
                                            lookup_merchant_use_case=lookup_merchant_use_case,
                                            build_inventory_table_use_case=build_inventory_table_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos")

        # Then
        ctx.send.assert_called_once_with("Where are the merchants?\n\nHere are the merchants.\n    Custom On (Weaponer)\n    Custom Or (Armorer)\n    Ensign Chant (General Goods)\n    Mr. Chant (General Goods)")

    async def test_shop__invalid_city(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()
        def mock_get_city_by_city_name_invalid(city_name):
            return None
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name_invalid

        lookup_city_use_case = LookupCityUseCase(mock_city_dao)

        shop_cog = ShopCog(bot, recipe_book(lookup_city_use_case=lookup_city_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Fakesville", "Mr.", "Chant")

        # Then
        ctx.send.assert_called_once_with("I'm not familiar with any city called Fakesville.")

    async def test_shop__not_in_city(self):
        # Given
        bot = MagicMock()

        mock_city_dao = Mock()

        def mock_get_city_by_city_name(city_name):
            return city(city_name, merchants=[merchant(merchant_name="Mr. Chant", inventory=[], sells_general_goods=InventoryType(True, None))], occupants=[1])
        mock_city_dao.get_city_by_city_name.side_effect = mock_get_city_by_city_name

        lookup_city_use_case = LookupCityUseCase(mock_city_dao)

        shop_cog = ShopCog(bot, recipe_book(lookup_city_use_case=lookup_city_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 2
        ctx.author.name = "fake_username_2"
        ctx.send = AsyncMock()

        # When
        await ShopCog.shop(shop_cog, ctx, "Qeynos", "Mr.", "Chant")

        # Then
        ctx.send.assert_called_once_with("You're not currently in Qeynos, so you cannot shop there.")