import logging

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from utils.autocomplete import filter_choices, filter_labelled_choices, city_choices_for_user, merchant_choices_for_city


_GUILD_IDS: list[int] = []


# ---------------------------------------------------------------------------
# Pagination View
# ---------------------------------------------------------------------------

class InventoryView(nextcord.ui.View):
    """
    Paginated embed view with Prev / Next buttons.
    Ephemeral — only the requesting user sees it.
    Times out after 3 minutes of inactivity.
    """

    def __init__(self, pages: list[nextcord.Embed]):
        super().__init__(timeout=180)
        self.pages = pages
        self.index = 0
        self._sync_buttons()

    def _sync_buttons(self):
        self.prev_button.disabled = self.index == 0
        self.next_button.disabled = self.index >= len(self.pages) - 1

    def _current_embed(self) -> nextcord.Embed:
        embed = self.pages[self.index]
        if len(self.pages) > 1:
            embed.set_footer(text=f"Page {self.index + 1} of {len(self.pages)}")
        return embed

    @nextcord.ui.button(label="◀  Prev", style=nextcord.ButtonStyle.secondary)
    async def prev_button(self, _button: nextcord.ui.Button, interaction: Interaction):
        self.index -= 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    @nextcord.ui.button(label="Next  ▶", style=nextcord.ButtonStyle.secondary)
    async def next_button(self, _button: nextcord.ui.Button, interaction: Interaction):
        self.index += 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def on_timeout(self):
        self.prev_button.disabled = True
        self.next_button.disabled = True
        self.stop()


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

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

    # ------------------------------------------------------------------
    # Autocomplete callbacks
    # ------------------------------------------------------------------

    @shop.on_autocomplete("city_name")
    async def autocomplete_city(self, interaction: Interaction, data: str):
        """Dropdown: cities the invoking user is an occupant of."""
        choices = city_choices_for_user(self.__recipe_book, interaction.user.id)
        await interaction.response.send_autocomplete(filter_choices(choices, data))

    @shop.on_autocomplete("merchant_name")
    async def autocomplete_merchant(self, interaction: Interaction, data: str):
        """
        Dropdown: merchants in the city the user has already filled in.
        """
        # Pull whatever city the user has typed/selected so far
        options = {
            opt["name"]: opt.get("value", "")
            for opt in interaction.data.get("options", [])
        }
        city_name = options.get("city", "")

        choices = merchant_choices_for_city(self.__recipe_book, city_name)
        await interaction.response.send_autocomplete(filter_labelled_choices(choices, data))

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    async def _handle_city(self, interaction: Interaction, city_name: str):
        embed = self.__recipe_book.build_inventory_table.build_city_merchants_embed(city_name)
        if embed is None:
            await interaction.followup.send(
                f"No city named **{city_name}** was found.", ephemeral=True
            )
            return
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _handle_inventory(
        self, interaction: Interaction, city_name: str, merchant_name: str
    ):
        pages = self.__recipe_book.build_inventory_table.build_merchant_inventory_embeds(
            city_name, merchant_name
        )
        if not pages:
            await interaction.followup.send(
                f"No merchant named **{merchant_name}** was found in **{city_name}**.",
                ephemeral=True,
            )
            return

        view = InventoryView(pages)
        await interaction.followup.send(
            embed=view._current_embed(), view=view, ephemeral=True
        )


def setup(bot: commands.Bot, recipe_book, guild_ids: list[int]):
    global _GUILD_IDS
    _GUILD_IDS.extend(guild_ids)
    bot.add_cog(ShopCog(bot, recipe_book))