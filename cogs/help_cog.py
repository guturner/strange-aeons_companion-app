from nextcord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        help_message = """
        ```Available Commands:
  !faction                           Calculate NPC reaction(s).
  !hail                              Setup your account.
  !shop [city_name]                  Search for merchants in a city.
  !shop [city_name] [merchant_name]  Browse a merchant's inventory.
  !whoami                            Confirm your account information.```"""

        await ctx.send(help_message)

def setup(bot):
    bot.add_cog(HelpCog(bot))