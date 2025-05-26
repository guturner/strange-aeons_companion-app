from nextcord.ext import commands

from results import LookupUserFailure, LookupUserSuccess


class WhoAmICog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def whoami(self, ctx):
        username = ctx.author.name

        lookup_user_result = self.__recipe_book.lookup_user.lookup_user_by_username(username)
        match lookup_user_result:
            case LookupUserSuccess(user=existing_user):
                if existing_user.user_id is None:
                    if existing_user.is_gm:
                        await ctx.send(
                            f"I believe you are our Game Master, {existing_user.player_first_name} {existing_user.player_last_name}, but try to [hail] me first.")
                    else:
                        await ctx.send(
                            f"I believe you are {existing_user.character_first_name}, but try to [hail] me first.")

                else:
                    if existing_user.is_gm:
                        await ctx.send(
                            f"You are our Game Master, of course, {existing_user.player_first_name} {existing_user.player_last_name}!")
                    else:
                        last_name_formatted = f" {existing_user.character_last_name}" if existing_user.character_last_name != "" else ""
                        await ctx.send(
                            f"Why, you are {existing_user.character_first_name}{last_name_formatted}, the level {existing_user.character_level} {existing_user.character_race} {existing_user.character_class}!")
            case LookupUserFailure():
                await ctx.send("You are not a player in this campaign.")

def setup(bot, recipe_book):
    bot.add_cog(WhoAmICog(bot, recipe_book))