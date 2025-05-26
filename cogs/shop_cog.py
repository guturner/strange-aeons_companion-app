from nextcord.ext import commands
from nextcord.ext.commands import MissingRequiredArgument

from results import BuildInventoryTableSuccess, BuildInventoryTableChunksSuccess, LookupCityFailure, LookupCitySuccess, LookupMerchantFailure


class ShopCog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.bot = bot
        self.__recipe_book = recipe_book

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, MissingRequiredArgument):
                await ctx.send(
                    f"You're missing a command argument: `{error.param.name}`\n"
                    f"Command Usage: `!shop [city_name] [merchant_name]`"
                )
            else:
                raise error

    @commands.command()
    async def shop(self, ctx, city_name, *merchant_name):
        user_id = ctx.author.id

        lookup_city_result = self.__recipe_book.lookup_city.lookup_city_by_city_name(city_name)
        match lookup_city_result:
            case LookupCitySuccess(city=found_city):
                if found_city.is_user_in_city(user_id):
                    if not merchant_name:
                        await ctx.send(found_city.directions.get_directions_string(sorted(found_city.merchants, key=lambda merchant: merchant.name)))

                    else:
                        formatted_merchant_name = " ".join(tuple(map(str.capitalize, merchant_name)))
                        build_table_result = self.__recipe_book.build_inventory_table.build_merchant_inventory_table(found_city.name, formatted_merchant_name)
                        match build_table_result:
                            case BuildInventoryTableSuccess(table=table):
                                await ctx.send(table)

                            case BuildInventoryTableChunksSuccess(table_chunks=inventory_table_chunks):
                                for table_chunk in inventory_table_chunks:
                                    await ctx.send(table_chunk)

                            case LookupMerchantFailure():
                                await ctx.send(found_city.directions.not_found.replace("{{merchant_name}}", formatted_merchant_name))
                else:
                    await ctx.send(f"You're not currently in {found_city.name}, so you cannot shop there.")

            case LookupCityFailure():
                await ctx.send(f"I'm not familiar with any city called {city_name.capitalize()}.")

def setup(bot, recipe_book):
    bot.add_cog(ShopCog(bot, recipe_book))