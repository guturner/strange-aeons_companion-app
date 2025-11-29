from nextcord.ext import commands


class ShopCog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def shop(self, ctx, city_name, *merchant_name):
        user_id = ctx.author.id

        city = self.__recipe_book.lookup_city.lookup_city_by_city_name(city_name)
        if city is not None:
            if city.is_user_in_city(user_id):
                if not merchant_name:
                    await ctx.send(city.directions.get_directions_string(sorted(city.merchants, key=lambda merchant: merchant.name)))

                else:
                    formatted_merchant_name = " ".join(tuple(map(str.capitalize, merchant_name)))
                    merchant_inventory_tables = self.__recipe_book.build_inventory_table.build_merchant_inventory_tables(city.name, formatted_merchant_name)
                    if merchant_inventory_tables is not None:
                        for table in merchant_inventory_tables:
                            await ctx.send(table)

                    else:
                        await ctx.send(city.directions.not_found.replace("{{merchant_name}}", formatted_merchant_name))
            else:
                await ctx.send(f"You're not currently in {city.name}, so you cannot shop there.")

        else:
            await ctx.send(f"I'm not familiar with any city called {city_name.capitalize()}.")

def setup(bot, recipe_book):
    bot.add_cog(ShopCog(bot, recipe_book))