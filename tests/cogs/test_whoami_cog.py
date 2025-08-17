import unittest

from unittest.mock import AsyncMock, MagicMock, Mock

from cogs.whoami_cog import WhoAmICog
from tests.utils import mock_get_user_by_user_id, mock_get_user_by_username, recipe_book
from use_cases.user_use_case import UserUseCase


class TestWhoAmICog(unittest.IsolatedAsyncioTestCase):
    async def test_whoami__gm__happy_path(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(user_use_case=user_use_case))

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
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(user_use_case=user_use_case))

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
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 2
        ctx.author.name = "fake_username_2"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Why, you are Tanner, the level 4 Half-Vah'Shir Bard!")

    async def test_whoami__not_found(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        shop_cog = WhoAmICog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 6
        ctx.author.name = "fake_username_6"
        ctx.send = AsyncMock()

        # When
        await WhoAmICog.whoami(shop_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("You are not a player in this campaign.")