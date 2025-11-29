from nextcord.ext import commands
from nextcord.ext.commands import MissingRequiredArgument


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, MissingRequiredArgument):
                await ctx.send(
                    f"You're missing a command argument: `{error.param.name}`\n"
                    f"Command Usage: `{self.bot.command_prefix}{ctx.command.qualified_name} [{error.param.name}]`"
                )
            else:
                raise error

def setup(bot):
    bot.add_cog(ErrorHandler(bot))