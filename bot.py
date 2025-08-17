import logging

import nextcord
import os
import re

from dotenv import load_dotenv
from nextcord.ext import commands

from cogs import hail_cog, help_cog, shop_cog, whoami_cog
from daos.city_dao import CityDAO
from daos.item_dao import ItemDAO
from daos.user_dao import UserDAO
from models.database import Database
from use_cases.build_inventory_table_use_case import BuildInventoryTableUseCase
from use_cases.build_table_use_case import BuildTableUseCase
from use_cases.lookup_city_use_case import LookupCityUseCase
from use_cases.lookup_inventory_use_case import LookupItemsUseCase
from use_cases.lookup_merchant_use_case import LookupMerchantUseCase
from use_cases.recipe_book import RecipeBook
from use_cases.user_use_case import UserUseCase


def __configure_logger():
    logging.basicConfig(
        level=logging.INFO,
        filename='logs.log',
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def __configure_intents():
    intents = nextcord.Intents.default()

    intents.dm_messages = True
    intents.messages = True
    intents.message_content = True

    return intents

def __configure_database(mongo_uri, database_name):
    return Database(mongo_uri, database_name)

def __configure_bot(bot):
    @bot.event
    async def on_command_error(ctx, error):
        logging.error(f"Error in command {ctx.command}, error: {error}")

    @bot.event
    async def on_message(message: nextcord.Message):
        logging.info(f"Received message: {message.content} from author: {message.author}.")
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return

        # Check if the message is in a DM channel
        if isinstance(message.channel, nextcord.DMChannel):
            if message.content.startswith(bot.command_prefix):
                await bot.process_commands(message)

            elif re.match(r"hail[\W_]*", message.content.upper(), re.IGNORECASE):
                ctx = await bot.get_context(message)
                await bot.get_command("hail").invoke(ctx)

            else:
                username = message.author.name
                await message.channel.send(
                    f"Hi {username}, if this is your first time using the EverQuest: Strange Aeons companion app, then try to "
                    f"[hail] me and I will setup your account; otherwise, use the `!help` command to see the list of commands you can use."
                )

def __main():
    load_dotenv(dotenv_path=".env.local", override=True)
    load_dotenv(dotenv_path=".env", override=False)

    __configure_logger()

    command_prefix = os.getenv("COMMAND_PREFIX")
    discord_token = os.getenv("DISCORD_TOKEN")
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("DB_NAME")

    intents = __configure_intents()
    bot = commands.Bot(command_prefix=command_prefix, intents=intents)

    database = __configure_database(mongo_uri, database_name)

    city_dao = CityDAO(database)
    inventory_dao = ItemDAO(database)
    user_dao = UserDAO(database)

    build_table_use_case = BuildTableUseCase()
    lookup_city_use_case = LookupCityUseCase(city_dao)
    lookup_inventory_use_case = LookupItemsUseCase(inventory_dao)
    lookup_merchant_use_case = LookupMerchantUseCase(lookup_city_use_case)
    build_inventory_table_use_case = BuildInventoryTableUseCase(lookup_merchant_use_case, lookup_inventory_use_case, build_table_use_case)
    user_use_case = UserUseCase(user_dao)

    recipe_book = RecipeBook(
        build_inventory_table_use_case=build_inventory_table_use_case,
        build_table_use_case=build_table_use_case,
        lookup_city_use_case=lookup_city_use_case,
        lookup_inventory_use_case=lookup_inventory_use_case,
        lookup_merchant_use_case=lookup_merchant_use_case,
        user_use_cases=user_use_case
    )

    __configure_bot(bot)

    # Remove the default help command
    bot.remove_command("help")

    # Load Commands
    help_cog.setup(bot)
    hail_cog.setup(bot, recipe_book)
    shop_cog.setup(bot, recipe_book)
    whoami_cog.setup(bot, recipe_book)

    bot.run(discord_token)

__main()