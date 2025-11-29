from nextcord.ext import commands


class FactionCog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def faction(self, ctx, player_alignment_input, *, faction_pair_input):
        try:
            faction_tables = self.__recipe_book.build_faction_table.build_faction_tables(player_alignment_input, faction_pair_input)
        except ValueError as e:
            await ctx.send(f"""{str(e)}
Command Usage: `!faction <PLAYER_ALIGNMENT> <FACTION_1_NAME> <FACTION_1_ALIGNMENT> <FACTION_2_NAME> <FACTION_2_ALIGNMENT>`
For example:
```!faction NG "The Guards" DG Bruisers NE```""")
            return

        for table in faction_tables:
            await ctx.send(table)

def setup(bot, recipe_book):
    bot.add_cog(FactionCog(bot, recipe_book))