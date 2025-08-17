import unittest
from unittest.mock import AsyncMock, MagicMock, Mock

from cogs.hail_cog import HailCog
from tests.utils import mock_get_user_by_user_id, recipe_book, mock_get_user_by_username, mock_update_user_by_username
from use_cases.user_use_case import UserUseCase


class TestHailCog(unittest.IsolatedAsyncioTestCase):
    async def test_hail__gm__happy_path(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id

        user_use_case = UserUseCase(mock_user_dao)

        hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 1
        ctx.author.name = "fake_username_1"
        ctx.send = AsyncMock()

        # When
        await HailCog.hail(hail_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Hail Game Master Turner.")

    async def test_hail__player__happy_path(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id

        user_use_case = UserUseCase(mock_user_dao)

        hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 2
        ctx.author.name = "fake_username_2"
        ctx.send = AsyncMock()

        # When
        await HailCog.hail(hail_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Hail Tanner.")

    async def test_hail__gm__not_registered(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username
        mock_user_dao.update_user_by_username.side_effect = mock_update_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 4
        ctx.author.name = "fake_username_4"
        ctx.send = AsyncMock()

        # When
        await HailCog.hail(hail_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Hail Game Master GM! You're all set, now let's get started.")

    async def test_hail__player__not_registered(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username
        mock_user_dao.update_user_by_username.side_effect = mock_update_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 5
        ctx.author.name = "fake_username_5"
        ctx.send = AsyncMock()

        # When
        await HailCog.hail(hail_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("Hail The, and welcome to Strange Aeons! You are all set.")

    async def test_hail__not_found(self):
        # Given
        bot = MagicMock()

        mock_user_dao = Mock()
        mock_user_dao.get_user_by_user_id.side_effect = mock_get_user_by_user_id
        mock_user_dao.get_user_by_username.side_effect = mock_get_user_by_username

        user_use_case = UserUseCase(mock_user_dao)

        hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

        ctx = MagicMock()
        ctx.author = MagicMock()
        ctx.author.id = 4
        ctx.author.name = "fake_username_6"
        ctx.send = AsyncMock()

        # When
        await HailCog.hail(hail_cog, ctx)

        # Then
        ctx.send.assert_called_once_with("You are not a player in this campaign.")