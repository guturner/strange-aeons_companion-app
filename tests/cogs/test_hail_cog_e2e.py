from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer
from unittest.mock import MagicMock, AsyncMock

from cogs.hail_cog import HailCog
from daos.user_dao import UserDAO
from models.database import Database
from tests.e2e_test import E2ETest
from tests.utils import recipe_book
from use_cases.user_use_case import UserUseCase


class TestHailCogE2E(E2ETest):
    async def __setup_environment(self, mongo):
        self.load_users_data(mongo)

    async def test_hail__gm__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            # Given
            bot = MagicMock()

            uri = mongo.get_connection_url()
            db_name = "everquest"
            mongo_client = MongoClient(uri)

            await self.__setup_environment(mongo)

            db = Database(uri, db_name)
            user_dao = UserDAO(db)

            user_use_case = UserUseCase(user_dao)

            hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

            ctx = MagicMock()
            ctx.author = MagicMock()
            ctx.author.id = 1
            ctx.author.name = "the_gm_1"
            ctx.send = AsyncMock()

            self.initialize_user(mongo_client, "the_gm_1", 1)

            # When
            await HailCog.hail(hail_cog, ctx)

            # Then
            ctx.send.assert_called_once_with("Hail Game Master GM.")

    async def test_hail__player__happy_path(self):
        with MongoDbContainer("mongo:8.0") as mongo:
            # Given
            bot = MagicMock()

            uri = mongo.get_connection_url()
            db_name = "everquest"
            mongo_client = MongoClient(uri)

            await self.__setup_environment(mongo)

            db = Database(uri, db_name)
            user_dao = UserDAO(db)

            user_use_case = UserUseCase(user_dao)

            hail_cog = HailCog(bot, recipe_book(user_use_case=user_use_case))

            ctx = MagicMock()
            ctx.author = MagicMock()
            ctx.author.id = 2
            ctx.author.name = "a_player_1"
            ctx.send = AsyncMock()

            self.initialize_user(mongo_client, "a_player_1", 2)

            # When
            await HailCog.hail(hail_cog, ctx)

            # Then
            ctx.send.assert_called_once_with("Hail The.")