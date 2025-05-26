import unittest
from unittest.mock import AsyncMock, MagicMock

from cogs.help_cog import HelpCog


class TestHelpCog(unittest.IsolatedAsyncioTestCase):
    async def test_help__happy_path(self):
        # Given
        bot = MagicMock()
        help_cog = HelpCog(bot)

        ctx = MagicMock()
        ctx.send = AsyncMock()

        # When
        await HelpCog.help(help_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("""
        ```Available Commands:
  !hail                              Setup your account.
  !shop [city_name]                  Search for merchants in a city.
  !shop [city_name] [merchant_name]  Browse a merchant's inventory.
  !whoami                            Confirm your account information.```""")
