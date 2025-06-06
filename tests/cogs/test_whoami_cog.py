import unittest

from unittest.mock import AsyncMock, MagicMock, Mock

from cogs.whoami_cog import WhoAmICog
from tests.utils import mock_get_user_by_username, recipe_book, user_guy, user_todd
from use_cases.lookup_user_use_case import LookupUserUseCase


class TestWhoAmICog(unittest.IsolatedAsyncioTestCase):
    async def test_whoami__gm__happy_path(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("You are our Game Master, of course, Guy Turner!")

    async def test_whoami__player__happy_path(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 3
        ctx.author.name = "fake_username_3"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Why, you are Keir Renwick, the level 4 Human Shadow Knight!")

    async def test_whoami__player__no_last_name(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 2
        ctx.author.name = "fake_username_2"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Why, you are Tanner, the level 4 Half-Vah'Shir Bard!")

    async def test_whoami__gm__not_registered(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        def mock_get_user_by_username_not_registered(username):
            user = user_guy()
            user.user_id = None
            return user
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username_not_registered

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("I believe you are our Game Master, Guy Turner, but try to [hail] me first.")

    async def test_whoami__player__not_registered(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        def mock_get_user_by_username_not_registered(username):
            user = user_todd()
            user.user_id = None
            return user
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username_not_registered

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("I believe you are Tanner, but try to [hail] me first.")

    async def test_whoami__not_found(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        def mock_get_user_by_username_not_found(username):
            return None
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username_not_found

        lookup_user_use_case = LookupUserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(lookup_user_use_case=lookup_user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 4
        ctx.author.name = "fake_username_4"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("You are not a player in this campaign.")