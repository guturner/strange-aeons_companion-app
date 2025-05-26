import copy

from nextcord.ext import commands

from results import LookupUserFailure, LookupUserSuccess, UpdateUserSuccess


class HailCog(commands.Cog):
    def __init__(self, bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

    @commands.command()
    async def hail(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        lookup_user_by_user_id_result = self.__recipe_book.lookup_user.lookup_user_by_user_id(user_id)
        match lookup_user_by_user_id_result:
            case LookupUserSuccess(user=existing_user):
                if existing_user.is_gm:
                    await ctx.send(f"Hail Game Master {existing_user.player_last_name}.")
                else:
                    await ctx.send(f"Hail {existing_user.character_first_name}.")

            case LookupUserFailure():
                lookup_user_by_username_result = self.__recipe_book.lookup_user.lookup_user_by_username(username)
                match lookup_user_by_username_result:
                    case LookupUserSuccess(user=user_template):
                        updated_user = copy.copy(user_template)
                        updated_user.user_id = user_id
                        update_user_result = self.__recipe_book.update_user.update_user_by_username(username=username, new_user=updated_user)
                        match update_user_result:
                            case UpdateUserSuccess(user=updated_user):
                                if updated_user.is_gm:
                                    await ctx.send(
                                        f"Hail Game Master {updated_user.player_last_name}! You're all set, now let's get started.")
                                else:
                                    await ctx.send(
                                        f"Hail {updated_user.character_first_name}, and welcome to Strange Aeons! You are all set.")

                    case LookupUserFailure():
                        await ctx.send("You are not a player in this campaign.")

def setup(bot, recipe_book):
    bot.add_cog(HailCog(bot, recipe_book))