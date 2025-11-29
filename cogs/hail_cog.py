from nextcord.ext import commands


class HailCog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def hail(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        (user, was_updated) = self.__recipe_book.user_use_cases.lookup_user(user_id=user_id, username=username)
        if user is None:
            await ctx.send("You are not a player in this campaign.")
        else:
            if user.is_gm:
                if was_updated:
                    await ctx.send(f"Hail Game Master {user.player_last_name}! You're all set, now let's get started.")
                else:
                    await ctx.send(f"Hail Game Master {user.player_last_name}.")
            else:
                if was_updated:
                    await ctx.send(f"Hail {user.character_first_name}, and welcome to Strange Aeons! You are all set.")
                else:
                    await ctx.send(f"Hail {user.character_first_name}.")

def setup(bot, recipe_book):
    bot.add_cog(HailCog(bot, recipe_book))