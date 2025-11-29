import unittest
from unittest.mock import MagicMock, AsyncMock

from cogs.faction_cog import FactionCog
from tests.utils import recipe_book
from use_cases.build_faction_table_use_case import BuildFactionTableUseCase
from use_cases.build_table_use_case import BuildTableUseCase
from use_cases.faction_use_case import FactionUseCase


class TestFactionCog(unittest.IsolatedAsyncioTestCase):
    async def test_faction__happy_path(self):
        # Given
        bot = MagicMock()

        build_table_use_case = BuildTableUseCase()
        faction_use_case = FactionUseCase()
        build_faction_table_use_case = BuildFactionTableUseCase(build_table_use_case, faction_use_case)

        faction_cog = FactionCog(bot, recipe_book(build_faction_table_use_case=build_faction_table_use_case, build_table_use_case=build_table_use_case, faction_use_case=faction_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await FactionCog.faction(faction_cog, ctx, "N", faction_pair_input="\"Some Faction\" N")

        # Then
        ctx.send.assert_called_once_with("```\n+------------------+--------------+-------------------+----------------------+------------------+\n| PLAYER ALIGNMENT | FACTION NAME | FACTION ALIGNMENT | ALIGNMENT COMPARISON | FACTION REACTION |\n+------------------+--------------+-------------------+----------------------+------------------+\n| N                | Some Faction | N                 | Same                 | Kind (+2)        |\n+------------------+--------------+-------------------+----------------------+------------------+```")

    async def test_faction__multiple_factions(self):
        # Given
        bot = MagicMock()

        build_table_use_case = BuildTableUseCase()
        faction_use_case = FactionUseCase()
        build_faction_table_use_case = BuildFactionTableUseCase(build_table_use_case, faction_use_case)

        faction_cog = FactionCog(bot, recipe_book(build_faction_table_use_case=build_faction_table_use_case,
                                                  build_table_use_case=build_table_use_case,
                                                  faction_use_case=faction_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await FactionCog.faction(faction_cog, ctx, "N", faction_pair_input="\"Some Faction\" N \"Some Other Faction\" OG")

        # Then
        ctx.send.assert_called_once_with("```\n+------------------+--------------------+-------------------+----------------------+------------------+\n| PLAYER ALIGNMENT | FACTION NAME       | FACTION ALIGNMENT | ALIGNMENT COMPARISON | FACTION REACTION |\n+------------------+--------------------+-------------------+----------------------+------------------+\n| N                | Some Faction       | N                 | Same                 | Kind (+2)        |\n| N                | Some Other Faction | OG                | Dissimilar           | Dubious (-4)     |\n+------------------+--------------------+-------------------+----------------------+------------------+```")


