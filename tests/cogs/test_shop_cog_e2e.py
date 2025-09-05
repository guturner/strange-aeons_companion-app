from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from unittest.mock import MagicMock, AsyncMock, call

from cogs.shop_cog import ShopCog
from daos.city_dao import CityDAO
from daos.item_dao import ItemDAO
from models.database import Database
from tests.e2e_test import E2ETest
from tests.utils import recipe_book
from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.build_table_use_case import BuildTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupItemsUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase


class TestShopCogE2E(E2ETest):
    async def __setup_environment(self, mongo):
        self.load_cities_data(mongo)
        self.load_items_data(mongo)
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
            item_dao = ItemDAO(db)

            build_table_use_case = BuildTableUseCase()
            lookup_city_use_case = LookupCityUseCase(city_dao)
            lookup_inventory_use_case = LookupItemsUseCase(item_dao)
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
            item_dao = ItemDAO(db)

            build_table_use_case = BuildTableUseCase()
            lookup_city_use_case = LookupCityUseCase(city_dao)
            lookup_inventory_use_case = LookupItemsUseCase(item_dao)
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
            ctx.send.assert_has_calls([call("```Clockwork Blacksmith II's Inventory (Part 1 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Axe, Throwing             | Melee Weapon | 8 GP    | -- | --      | --  | 1D6  | x2        | Standard | Small, Martial  | 10 ft. Range Increment   |\n| Banded Mail               | Armor        | 250 GP  | +6 | +1      | -6  | --   | --        | --       | Heavy           | --                       |\n| Battleaxe                 | Melee Weapon | 10 GP   | -- | --      | --  | 1D8  | x3        | Standard | Medium, Martial | --                       |\n| Brass Knuckles            | Melee Weapon | 1 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Tiny, Simple    | --                       |\n| Broad Sword               | Melee Weapon | 13 GP   | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | --                       |\n| Broad Sword (Masterwork)  | Melee Weapon | 313 GP  | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | Atk +1 (non-magical)     |\n| Broad Sword, +1           | Melee Weapon | 2313 GP | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | Atk +1, Dmg +1 (magical) |\n| Chain, Spiked             | Melee Weapon | 325 GP  | -- | --      | --  | 2D4  | x2        | Standard | Large, Martial  | 10 ft. Reach             |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 2 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Clawed Handwrap           | Melee Weapon | 12 GP   | -- | --      | --  | 1D4  | x2        | Quick    | Small, Martial  | --                       |\n| Club                      | Melee Weapon | 3 GP    | -- | --      | --  | 1D6  | x2        | Standard | Medium, Simple  | 10 ft. Range Increment   |\n| Dagger                    | Melee Weapon | 2 GP    | -- | --      | --  | 1D3  | 19-20, x2 | Quick    | Tiny, Simple    | 10 ft. Range Increment   |\n| Dagger, Punching          | Melee Weapon | 2 GP    | -- | --      | --  | 1D3  | x3        | Quick    | Tiny, Simple    | --                       |\n| Falchion                  | Melee Weapon | 75 GP   | -- | --      | --  | 2D4  | 18-20, x2 | Standard | Large, Martial  | --                       |\n| Flail, Heavy              | Melee Weapon | 15 GP   | -- | --      | --  | 1D10 | 19-20, x2 | Standard | Large, Martial  | --                       |\n| Flail, Light              | Melee Weapon | 8 GP    | -- | --      | --  | 1D8  | x2        | Standard | Medium, Martial | --                       |\n| Full Plate                | Armor        | 1500 GP | +8 | +1      | -6  | --   | --        | --       | Heavy           | --                       |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 3 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Full Plate (Masterwork)   | Armor        | 1650 GP | +8 | +1      | -5  | --   | --        | --       | Heavy           | --                       |\n| Full Plate, +1            | Armor        | 2650 GP | +9 | +1      | -5  | --   | --        | --       | Heavy           | --                       |\n| Gauntlet (Large)          | Melee Weapon | 2 GP    | -- | --      | --  | 1D4  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet (Medium-size)    | Melee Weapon | 2 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet (Small)          | Melee Weapon | 2 GP    | -- | --      | --  | 1D2  | x2        | Quick    | Unarmed, Simple | --                       |\n| Gauntlet Spiked           | Melee Weapon | 5 GP    | -- | --      | --  | 1D3  | x2        | Quick    | Tiny, Simple    | --                       |\n| Glaive                    | Melee Weapon | 8 GP    | -- | --      | --  | 1D12 | x3        | Slow     | Large, Martial  | 10 ft. Reach             |\n| Greataxe                  | Melee Weapon | 20 GP   | -- | --      | --  | 2D6  | x3        | Slow     | Large, Martial  | --                       |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 4 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Greatclub                 | Melee Weapon | 5 GP    | -- | --      | --  | 1D12 | x2        | Slow     | Large, Martial  | --                       |\n| Greatsword                | Melee Weapon | 50 GP   | -- | --      | --  | 2D6  | 19-20, x2 | Slow     | Large, Martial  | --                       |\n| Guisarme                  | Melee Weapon | 9 GP    | -- | --      | --  | 2D4  | x3        | Standard | Large, Martial  | 10 ft. Reach             |\n| Halberd                   | Melee Weapon | 10 GP   | -- | --      | --  | 1D12 | x3        | Slow     | Large, Martial  | --                       |\n| Half-Plate                | Armor        | 600 GP  | +7 | +0      | -7  | --   | --        | --       | Heavy           | --                       |\n| Half-Plate (Masterwork)   | Armor        | 750 GP  | +7 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Half-Plate, +1            | Armor        | 1750 GP | +8 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Hammer, Light             | Melee Weapon | 1 GP    | -- | --      | --  | 1D4  | x2        | Standard | Small, Martial  | 20 ft. Range Increment   |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 5 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Handaxe                   | Melee Weapon | 6 GP    | -- | --      | --  | 1D6  | x3        | Standard | Small, Martial  | --                       |\n| Javelin                   | Melee Weapon | 1 GP    | -- | --      | --  | 1D6  | x2        | Standard | Medium, Simple  | 30 ft. Range Increment   |\n| Kama                      | Melee Weapon | 2 GP    | -- | --      | --  | 1D4  | x2        | Quick    | Small, Martial  | --                       |\n| Kukri                     | Melee Weapon | 8 GP    | -- | --      | --  | 1D4  | 18-20, x2 | Standard | Tiny, Martial   | --                       |\n| Longspear                 | Melee Weapon | 5 GP    | -- | --      | --  | 1D8  | x3        | Standard | Large, Martial  | 10 ft. Reach             |\n| Mace, Heavy               | Melee Weapon | 12 GP   | -- | --      | --  | 1D8  | x2        | Standard | Medium, Simple  | --                       |\n| Mace, Light               | Melee Weapon | 5 GP    | -- | --      | --  | 1D6  | x2        | Standard | Small, Simple   | --                       |\n| Morningstar               | Melee Weapon | 8 GP    | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Simple  | --                       |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 6 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Splint Mail               | Armor        | 200 GP  | +6 | +0      | -7  | --   | --        | --       | Heavy           | --                       |\n| Splint Mail (Masterwork)  | Armor        | 350 GP  | +6 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Splint Mail, +1           | Armor        | 1350 GP | +7 | +0      | -6  | --   | --        | --       | Heavy           | --                       |\n| Sword, Bastard            | Melee Weapon | 35 GP   | -- | --      | --  | 1D10 | 19-20, x2 | Standard | Large, Martial  | --                       |\n| Sword, Short              | Melee Weapon | 10 GP   | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | --                       |\n| Sword, Short (Masterwork) | Melee Weapon | 310 GP  | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | Atk +1 (non-magical)     |\n| Sword, Short, +1          | Melee Weapon | 2310 GP | -- | --      | --  | 1D6  | 19-20, x2 | Standard | Small, Martial  | Atk +1, Dmg +1 (magical) |\n| Trident                   | Melee Weapon | 15 GP   | -- | --      | --  | 1D10 | x2        | Slow     | Medium, Martial | 10 ft. Range Increment   |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```"),
                call("```Clockwork Blacksmith II's Inventory (Part 7 / 7):\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| NAME                      | TYPE         | COST    | AC | MAX DEX | ACP | DMG  | CRIT      | DELAY    | SIZE            | STATS                    |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+\n| Two-Handed Hammer         | Melee Weapon | 20 GP   | -- | --      | --  | 2D6  | x2        | Slow     | Large, Martial  | --                       |\n| Warhammer                 | Melee Weapon | 12 GP   | -- | --      | --  | 1D8  | x3        | Standard | Medium, Martial | --                       |\n+---------------------------+--------------+---------+----+---------+-----+------+-----------+----------+-----------------+--------------------------+```")
            ])

    async def test_shop__spells__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            # Given
            bot = MagicMock()

            uri = mongo.get_connection_url()
            db_name = "everquest"
            mongo_client = MongoClient(uri)

            await self.__setup_environment(mongo)

            db = Database(uri, db_name)
            city_dao = CityDAO(db)
            item_dao = ItemDAO(db)

            build_table_use_case = BuildTableUseCase()
            lookup_city_use_case = LookupCityUseCase(city_dao)
            lookup_inventory_use_case = LookupItemsUseCase(item_dao)
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
            await ShopCog.shop(shop_cog, ctx, "Ak'Anon", "Clockwork", "Merchant", "XVI")

            # Then
            ctx.send.assert_has_calls([call("```Clockwork Merchant XVI's Inventory (Part 1 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Burn                   | Spell | 100 GP | Mag 2                                           | 1D10 fire dmg (1 creature)                                             |\n| Cure Disease           | Spell | 25 GP  | Bst 1, Clr 2, Dru 2, Nec 5, Pal 2, Shm 1        | Removes 1 [disease] effect (1 creature)                                |\n| Cure Poison            | Spell | 25 GP  | Bst 2, Clr 1, Dru 2, Pal 1, Rng 2, Shm 2        | Removes 1 [poison] effect (1 creature)                                 |\n| Despair                | Spell | 25 GP  | Shd 1                                           | -1 Atk (1 creature)                                                    |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 2 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Disease Cloud          | Spell | 25 GP  | Nec 1, Shd 1                                    | 1 HP disease dmg immediately, then every 2nd round (1 creature)        |\n| Elementaling: Air      | Spell | 225 GP | Mag 3                                           | Summons an Air Elemental (Type 2)                                      |\n| Elementaling: Earth    | Spell | 225 GP | Mag 3                                           | Summons an Earth Elemental (Type 2)                                    |\n| Elementaling: Fire     | Spell | 225 GP | Mag 3                                           | Summons a Fire Elemental (Type 2)                                      |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 3 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Elementaling: Water    | Spell | 225 GP | Mag 3                                           | Summons a Water Elemental (Type 2)                                     |\n| Elementalkin: Air      | Spell | 100 GP | Mag 2                                           | Summons an Air Elemental (Type 1)                                      |\n| Elementalkin: Earth    | Spell | 100 GP | Mag 2                                           | Summons an Earth Elemental (Type 1)                                    |\n| Elementalkin: Fire     | Spell | 100 GP | Mag 2                                           | Summons a Fire Elemental (Type 1)                                      |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 4 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Elementalkin: Water    | Spell | 100 GP | Mag 2                                           | Summons a Water Elemental (Type 1)                                     |\n| Endure Cold            | Spell | 25 GP  | Bst 1, Clr 4, Dru 3, Nec 1, Rng 3, Shd 2, Shm 1 | Cold Resistance (8), Cold Save +2 (1 creature)                         |\n| Flame Bolt             | Spell | 225 GP | Mag 3                                           | 3D10 fire dmg (1 creature, ranged touch atk)                           |\n| Invisibility           | Spell | 225 GP | Bst 6, Enc 2, Mag 3, Shm 8, Wiz 5               | Invisibility (excluding undead) (1 creature)                           |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 5 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Invisibility to Undead | Spell | 25 GP  | Clr 4, Enc 5, Nec 1, Pal 3, Shd 1, Wiz 9        | Invisibility (only undead) (self for Shd & Wiz; 1 creature for others) |\n| Leering Corpse         | Spell | 25 GP  | Nec 2, Shd 1                                    | Summons a Skeleton (Type 2)                                            |\n| Lesser Shielding       | Spell | 225 GP | Enc 3, Mag 3, Nec 3, Wiz 3                      | +3 AC, +7 HP, magic resistance (4), magic save +1 (self)               |\n| Lifetap                | Spell | 25 GP  | Nec 1, Shd 1                                    | 2 HP magic dmg (ref half dmg) (1 creature), cures 2 HP (self)          |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 6 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Minor Healing          | Spell | 25 GP  | Bst 1, Clr 1, Dru 1, Pal 1, Rng 1, Shm 1        | Cures 1D10 HP (1 creature)                                             |\n| Minor Shielding        | Spell | 25 GP  | Enc 1, Mag 1, Nec 1, Wiz 1                      | +2 AC, +2 HP (self)                                                    |\n| Renew Elements         | Spell | 225 GP | Mag 3                                           | Cures 3D10 HP (pet only)                                               |\n| Shield of Fire         | Spell | 225 GP | Mag 3                                           | Fire resistance (4), fire save +1, damage shield (2) (1 creature)      |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```"),
                call("```Clockwork Merchant XVI's Inventory (Part 7 / 7):\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| NAME                   | TYPE  | COST   | LVL                                             | DESCRIPTION                                                            |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+\n| Shock of Blades        | Spell | 225 GP | Mag 3                                           | 3D8 magic slashing dmg (ref half dmg, interrupts on fail)              |\n| Staff of Tracing       | Spell | 225 GP | Mag 3                                           | Summons a magic quarterstaff with 2 charges of +2 Con (self, 1 min)    |\n+------------------------+-------+--------+-------------------------------------------------+------------------------------------------------------------------------+```")
            ])