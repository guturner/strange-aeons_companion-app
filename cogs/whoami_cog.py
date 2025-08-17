from nextcord.ext import commands


class WhoAmICog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def whoami(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        (user, _) = self.__recipe_book.user_use_cases.lookup_user(user_id=user_id, username=username)
        if user is not None:
            if user.is_gm:
                await ctx.send(f"You are our Game Master, of course, {user.player_first_name} {user.player_last_name}!")
            else:
                last_name_formatted = f" {user.character_last_name}" if user.character_last_name != "" else ""
                await ctx.send(
                    f"Why, you are {user.character_first_name}{last_name_formatted}, the level {user.character_level} {user.character_race} {user.character_class}!")
        else:
            await ctx.send("You are not a player in this campaign.")

def setup(bot, recipe_book):
    bot.add_cog(WhoAmICog(bot, recipe_book))