from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from unittest.mock import MagicMock, AsyncMock, call

from cogs.shop_cog import ShopCog
from daos.city_dao import CityDAO
from daos.inventory_dao import InventoryDAO
from models.database import Database
from tests.e2e_test import E2ETest
from tests.utils import recipe_book
from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.build_table_use_case import BuildTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupInventoryUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase


class TestShopCogE2E(E2ETest):
    async def __setup_environment(self, mongo):
        self.load_cities_data(mongo)
        self.load_inventories_data(mongo)
        self.load_users_data(mongo)

    async def test_shop__general_goods__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            # Given
            bot = MagicMock()

            uri = mongo.get_connection_url()
            db_name = "everquest"
            mongo_client = MongoClient(uri)

            await self.__setup_environment(mongo)

            db = Database(uri, db_name)
            city_dao = CityDAO(db)
            inventory_dao = InventoryDAO(db)

            build_table_use_case = BuildTableUseCase()
            lookup_city_use_case = LookupCityUseCase(city_dao)
            lookup_inventory_use_case = LookupInventoryUseCase(inventory_dao)
            lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
            build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

            shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case,
                                                lookup_city_use_case=lookup_city_use_case,
                                                lookup_inventory_use_case=lookup_inventory_use_case,
                                                lookup_merchant_use_case=lookup_merchant_use_case,
                                                build_inventory_table_use_case=build_inventory_table_use_case))

            ctx = MagicMock()
            ctx.author = MagicMock()
            ctx.author.id = 2
            ctx.author.name = "a_player_1"
            ctx.send = AsyncMock()

            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            # When
            await ShopCog.shop(shop_cog, ctx, "Ak'Anon", "Clockwork", "Merchant", "XXIII")

            # Then
            ctx.send.assert_has_calls([
                call("```Clockwork Merchant XXIII's Inventory (Part 1 / 4):\n+--------------------------+--------------+-------+\n| NAME                     | TYPE         | COST  |\n+--------------------------+--------------+-------+\n| Bedroll                  | General Good | 1 SP  |\n| Bell                     | General Good | 1 GP  |\n| Blanket, Winter          | General Good | 5 SP  |\n| Bottle                   | General Good | 2 GP  |\n| Bucket                   | General Good | 5 SP  |\n| Candle                   | General Good | 1 CP  |\n| Canvas (1 sq. yd.)       | General Good | 1 SP  |\n| Case (Map or Scroll)     | General Good | 1 GP  |\n| Chain (10 ft.)           | General Good | 30 GP |\n| Chalk, 1 piece           | General Good | 1 CP  |\n+--------------------------+--------------+-------+```"),
                call("```Clockwork Merchant XXIII's Inventory (Part 2 / 4):\n+--------------------------+--------------+-------+\n| NAME                     | TYPE         | COST  |\n+--------------------------+--------------+-------+\n| Crowbar                  | General Good | 2 GP  |\n| Fishing Net (25 sq. ft.) | General Good | 4 GP  |\n| Fishing Pole             | General Good | 4 SP  |\n| Flask                    | General Good | 3 SP  |\n| Flint and Steel          | General Good | 1 GP  |\n| Grappling Hook           | General Good | 1 GP  |\n| Hammer                   | General Good | 5 SP  |\n| Ink (1 oz. vial)         | General Good | 8 GP  |\n| Ink Pen                  | General Good | 1 SP  |\n| Lamp                     | General Good | 1 SP  |\n+--------------------------+--------------+-------+```"),
                call("```Clockwork Merchant XXIII's Inventory (Part 3 / 4):\n+--------------------------+--------------+-------+\n| NAME                     | TYPE         | COST  |\n+--------------------------+--------------+-------+\n| Mirror                   | General Good | 10 GP |\n| Oil (1 pint flask)       | General Good | 1 SP  |\n| Parchment (1 sheet)      | General Good | 2 SP  |\n| Rations (per day)        | General Good | 5 SP  |\n| Rope, Hemp (50 ft.)      | General Good | 1 GP  |\n| Rope, Silk (50 ft.)      | General Good | 10 GP |\n| Sealing Wax              | General Good | 1 GP  |\n| Sewing Needle            | General Good | 5 SP  |\n| Signal Whistle           | General Good | 8 SP  |\n| Soap (1 lb)              | General Good | 5 SP  |\n+--------------------------+--------------+-------+```"),
                call("```Clockwork Merchant XXIII's Inventory (Part 4 / 4):\n+--------------------------+--------------+-------+\n| NAME                     | TYPE         | COST  |\n+--------------------------+--------------+-------+\n| Spade                    | General Good | 2 GP  |\n| Torch                    | General Good | 1 CP  |\n| Water Skin               | General Good | 1 GP  |\n+--------------------------+--------------+-------+```")
            ])

    async def test_shop__weapons__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            # Given
            bot = MagicMock()

            uri = mongo.get_connection_url()
            db_name = "everquest"
            mongo_client = MongoClient(uri)

            await self.__setup_environment(mongo)

            db = Database(uri, db_name)
            city_dao = CityDAO(db)
            inventory_dao = InventoryDAO(db)

            build_table_use_case = BuildTableUseCase()
            lookup_city_use_case = LookupCityUseCase(city_dao)
            lookup_inventory_use_case = LookupInventoryUseCase(inventory_dao)
            lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
            build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)

            shop_cog = ShopCog(bot, recipe_book(build_table_use_case=build_table_use_case,
                                                lookup_city_use_case=lookup_city_use_case,
                                                lookup_inventory_use_case=lookup_inventory_use_case,
                                                lookup_merchant_use_case=lookup_merchant_use_case,
                                                build_inventory_table_use_case=build_inventory_table_use_case))

            ctx = MagicMock()
            ctx.author = MagicMock()
            ctx.author.id = 2
            ctx.author.name = "a_player_1"
            ctx.send = AsyncMock()

            self.initialize_user(mongo_client, "a_player_1", 2)
            self.set_city_occupants(mongo_client, "Ak'Anon", [2])

            # When
            await ShopCog.shop(shop_cog, ctx, "Ak'Anon", "Clockwork", "Blacksmith", "II")

            # Then
            ctx.send.assert_has_calls([
                call("```Clockwork Blacksmith II's Inventory (Part 1 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Axe, Throwing             | Weapon | 8 GP    | -- | --      | --  | 1D6  | x2        | Standard | Small, Martial  | 10 ft. Range Increment   |\n| Banded Mail               | Armor  | 250 GP  | +6 | +1      | -6  | --   | --        | --       | Heavy           | --                       |\n| Battleaxe                 | Weapon | 10 GP   | -- | --      | --  | 1D8  | x3        | Standard | Medium, Martial | --                       |\n| Brass Knuckles            | Weapon | 1 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Tiny, Simple    | --                       |\n| Broad Sword               | Weapon | 13 GP   | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | --                       |\n| Broad Sword (Masterwork)  | Weapon | 313 GP  | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | Atk +1 (non-magical)     |\n| Broad Sword, +1           | Weapon | 2313 GP | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | Atk +1, Dmg +1 (magical) |\n| Chain, Spiked             | Weapon | 325 GP  | -- | --      | --  | 2D4  | x2        | Standard | Large, Martial  | 10 ft. Reach             |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 2 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Clawed Handwrap           | Weapon | 12 GP   | -- | --      | --  | 1D4  | x2        | Quick    | Small, Martial  | --                       |\n| Club                      | Weapon | 3 GP    | -- | --      | --  | 1D6  | x2        | Standard | Medium, Simple  | 10 ft. Range Increment   |\n| Dagger                    | Weapon | 2 GP    | -- | --      | --  | 1D3  | 19-20, x2 | Quick    | Tiny, Simple    | 10 ft. Range Increment   |\n| Dagger, Punching          | Weapon | 2 GP    | -- | --      | --  | 1D3  | x3        | Quick    | Tiny, Simple    | --                       |\n| Falchion                  | Weapon | 75 GP   | -- | --      | --  | 2D4  | 18-20, x2 | Standard | Large, Martial  | --                       |\n| Flail, Heavy              | Weapon | 15 GP   | -- | --      | --  | 1D10 | 19-20, x2 | Standard | Large, Martial  | --                       |\n| Flail, Light              | Weapon | 8 GP    | -- | --      | --  | 1D8  | x2        | Standard | Medium, Martial | --                       |\n| Full Plate                | Armor  | 1500 GP | +8 | +1      | -6  | --   | --        | --       | Heavy           | --                       |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 3 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Full Plate (Masterwork)   | Armor  | 1650 GP | +8 | +1      | -5  | --   | --        | --       | Heavy           | --                       |\n| Full Plate, +1            | Armor  | 2650 GP | +9 | +1      | -5  | --   | --        | --       | Heavy           | --                       |\n| Gauntlet (Large)          | Weapon | 2 GP    | -- | --      | --  | 1D4  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet (Medium-size)    | Weapon | 2 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet (Small)          | Weapon | 2 GP    | -- | --      | --  | 1D2  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet Spiked           | Weapon | 5 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Tiny, Simple    | --                       |\n| Glaive                    | Weapon | 8 GP    | -- | --      | --  | 1D12 | x3        | Slow     | Large, Martial  | 10 ft. Reach             |\n| Greataxe                  | Weapon | 20 GP   | -- | --      | --  | 2D6  | x3        | Slow     | Large, Martial  | --                       |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 4 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Greatclub                 | Weapon | 5 GP    | -- | --      | --  | 1D12 | x2        | Slow     | Large, Martial  | --                       |\n| Greatsword                | Weapon | 50 GP   | -- | --      | --  | 2D6  | 19-20, x2 | Slow     | Large, Martial  | --                       |\n| Guisarme                  | Weapon | 9 GP    | -- | --      | --  | 2D4  | x3        | Standard | Large, Martial  | 10 ft. Reach             |\n| Halberd                   | Weapon | 10 GP   | -- | --      | --  | 1D12 | x3        | Slow     | Large, Martial  | --                       |\n| Half-Plate                | Armor  | 600 GP  | +7 | +0      | -7  | --   | --        | --       | Heavy           | --                       |\n| Half-Plate (Masterwork)   | Armor  | 750 GP  | +7 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Half-Plate, +1            | Armor  | 1750 GP | +8 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Hammer, Light             | Weapon | 1 GP    | -- | --      | --  | 1D4  | x2        | Standard | Small, Martial  | 20 ft. Range Increment   |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 5 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Handaxe                   | Weapon | 6 GP    | -- | --      | --  | 1D6  | x3        | Standard | Small, Martial  | --                       |\n| Javelin                   | Weapon | 1 GP    | -- | --      | --  | 1D6  | x2        | Standard | Medium, Simple  | 30 ft. Range Increment   |\n| Kama                      | Weapon | 2 GP    | -- | --      | --  | 1D4  | x2        | Quick    | Small, Martial  | --                       |\n| Kukri                     | Weapon | 8 GP    | -- | --      | --  | 1D4  | 18-20, x2 | Standard | Tiny, Martial   | --                       |\n| Longspear                 | Weapon | 5 GP    | -- | --      | --  | 1D8  | x3        | Standard | Large, Martial  | 10 ft. Reach             |\n| Mace, Heavy               | Weapon | 12 GP   | -- | --      | --  | 1D8  | x2        | Standard | Medium, Simple  | --                       |\n| Mace, Light               | Weapon | 5 GP    | -- | --      | --  | 1D6  | x2        | Standard | Small, Simple   | --                       |\n| Morningstar               | Weapon | 8 GP    | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Simple  | --                       |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 6 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Splint Mail               | Armor  | 200 GP  | +6 | +0      | -7  | --   | --        | --       | Heavy           | --                       |\n| Splint Mail (Masterwork)  | Armor  | 350 GP  | +6 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Splint Mail, +1           | Armor  | 1350 GP | +7 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Sword, Bastard            | Weapon | 35 GP   | -- | --      | --  | 1D10 | 19-20, x2 | Standard | Large, Martial  | --                       |\n| Sword, Short              | Weapon | 10 GP   | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | --                       |\n| Sword, Short (Masterwork) | Weapon | 310 GP  | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | Atk +1 (non-magical)     |\n| Sword, Short, +1          | Weapon | 2310 GP | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | Atk +1, Dmg +1 (magical) |\n| Trident                   | Weapon | 15 GP   | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | 10 ft. Range Increment   |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 7 / 7):\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE   | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Two-Handed Hammer         | Weapon | 20 GP   | -- | --      | --  | 2D6  | x2        | Slow     | Large, Martial  | --                       |\n| Warhammer                 | Weapon | 12 GP   | -- | --      | --  | 1D8  | x3        | Standard | Medium, Martial | --                       |\n+---------------------------+--------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```")
            ])