import logging

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from utils.autocomplete import filter_choices, filter_labelled_choices, city_choices_for_user, merchant_choices_for_city
from models.pagination import PaginatedView


_GUILD_IDS: list[int] = []


class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

    @property
    def recipe_book(self):
        """Exposed for testing — avoids name-mangled attribute access."""
        return self.__recipe_book

    # -----------------------------------------------------------------------
    # Internal implementation — called directly by tests to bypass the
    # nextcord slash-command decorator wrapper.
    # -----------------------------------------------------------------------

    async def _shop_impl(
        self,
        interaction: Interaction,
        city_name: str,
        merchant_name: str | None = None,
    ):
        """
        Core shop logic. Separated from the slash-command decorator so that
        unit tests can call it directly without triggering nextcord's argument
        injection, which causes "multiple values for argument" errors.
        """
        await interaction.response.defer(ephemeral=True)

        try:
            if merchant_name:
                await self._handle_inventory(interaction, city_name, merchant_name)
            else:
                await self._handle_city(interaction, city_name)
        except Exception as exc:
            logging.error(f"/shop error: {exc}", exc_info=True)
            await interaction.followup.send(
                "Something went wrong. Please try again.", ephemeral=True
            )

    # -----------------------------------------------------------------------
    # Slash command — thin wrapper that delegates to _shop_impl
    # -----------------------------------------------------------------------

    @nextcord.slash_command(
        name="shop",
        description="Browse merchants or a merchant's inventory in a city.",
        guild_ids=_GUILD_IDS,
    )
    async def shop(
        self,
        interaction: Interaction,
        city_name: str = SlashOption(
            name="city",
            description="Your city (shows cities you occupy)",
            required=True,
            autocomplete=True,
        ),
        merchant_name: str = SlashOption(
            name="merchant",
            description="Merchant name (leave blank to list all merchants)",
            required=False,
            default=None,
            autocomplete=True,
        ),
    ):
        await self._shop_impl(interaction, city_name=city_name, merchant_name=merchant_name)

    # -----------------------------------------------------------------------
    # Autocomplete callbacks
    # -----------------------------------------------------------------------

    @shop.on_autocomplete("city_name")
    async def autocomplete_city(self, interaction: Interaction, data: str):
        """Dropdown: cities the invoking user is an occupant of."""
        choices = city_choices_for_user(self.__recipe_book, interaction.user.id)
        await interaction.response.send_autocomplete(filter_choices(choices, data))

    @shop.on_autocomplete("merchant_name")
    async def autocomplete_merchant(self, interaction: Interaction, data: str):
        """Dropdown: merchants in the city the user has already filled in."""
        options = {
            opt["name"]: opt.get("value", "")
            for opt in interaction.data.get("options", [])
        }
        city_name = options.get("city", "")
        choices = merchant_choices_for_city(self.__recipe_book, city_name)
        await interaction.response.send_autocomplete(filter_labelled_choices(choices, data))

    # -----------------------------------------------------------------------
    # Internal handlers
    # -----------------------------------------------------------------------

    async def _handle_city(self, interaction: Interaction, city_name: str):
        """Shows the merchant listing for a city."""
        # City lookup lives in the cog layer — BuildInventoryTableUseCase
        # no longer holds a city DAO reference.
        lookup_city = self.__recipe_book.lookup_city
        embed = self.__recipe_book.build_inventory_table.build_city_merchants_embed(
            city_name, lookup_city
        )
        if embed is None:
            await interaction.followup.send(
                f"No city named **{city_name}** was found.", ephemeral=True
            )
            return
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _handle_inventory(
        self, interaction: Interaction, city_name: str, merchant_name: str
    ):
        """Shows paginated inventory for a specific merchant."""
        pages = self.__recipe_book.build_inventory_table.build_merchant_inventory_embeds(
            city_name, merchant_name
        )
        if not pages:
            await interaction.followup.send(
                f"No merchant named **{merchant_name}** was found in **{city_name}**.",
                ephemeral=True,
            )
            return

        if len(pages) == 1:
            await interaction.followup.send(embed=pages[0], ephemeral=True)
        else:
            view = PaginatedView(pages)
            await interaction.followup.send(
                embed=view.current_embed(), view=view, ephemeral=True
            )


def setup(bot: commands.Bot, recipe_book, guild_ids: list[int]):
    global _GUILD_IDS
    _GUILD_IDS.extend(guild_ids)
    bot.add_cog(ShopCog(bot, recipe_book))