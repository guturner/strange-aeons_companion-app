import logging

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands


# ---------------------------------------------------------------------------
# Pagination View
# ---------------------------------------------------------------------------

class InventoryView(nextcord.ui.View):
    """
    A paginated embed view with Prev / Next buttons.
    Sent ephemerally so only the requesting user sees it.
    Times out after 3 minutes of inactivity.
    """

    def __init__(self, pages: list[nextcord.Embed]):
        super().__init__(timeout=180)
        self.pages = pages
        self.index = 0
        self._sync_buttons()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _sync_buttons(self):
        self.prev_button.disabled = self.index == 0
        self.next_button.disabled = self.index >= len(self.pages) - 1

    def _current_embed(self) -> nextcord.Embed:
        embed = self.pages[self.index]
        if len(self.pages) > 1:
            embed.set_footer(text=f"Page {self.index + 1} of {len(self.pages)}")
        return embed

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Timeout — disable buttons so the embed doesn't show dead controls
    # ------------------------------------------------------------------

    async def on_timeout(self):
        self.prev_button.disabled = True
        self.next_button.disabled = True
        self.stop()


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

GUILD_IDS_ENV_KEY = "GUILD_ID"  # set in .env as a comma-separated list if needed


class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot, recipe_book, guild_ids: list[int]):
        self.__bot = bot
        self.__recipe_book = recipe_book
        self.__guild_ids = guild_ids

    # ------------------------------------------------------------------
    # /shop  (city_name only) — list merchants
    # /shop  (city_name + merchant_name) — show paginated inventory
    # ------------------------------------------------------------------

    @nextcord.slash_command(
        name="shop",
        description="Browse merchants or a merchant's inventory in a city.",
    )
    async def shop(
        self,
        interaction: Interaction,
        city_name: str = SlashOption(
            name="city",
            description="Name of the city (e.g. Kelethin)",
            required=True,
        ),
        merchant_name: str = SlashOption(
            name="merchant",
            description="Name of the merchant (leave blank to list all merchants)",
            required=False,
            default=None,
        ),
    ):
        # Defer immediately — embed builds can take a moment with DB calls.
        # ephemeral=True means only the invoking user sees the response.
        await interaction.response.defer(ephemeral=True)

        logging.info(
            f"/shop invoked by {interaction.user} | city={city_name!r} merchant={merchant_name!r}"
        )

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
    # Internal handlers
    # ------------------------------------------------------------------

    async def _handle_city(self, interaction: Interaction, city_name: str):
        """Show the merchant list for a city."""
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
        """Show paginated inventory for a specific merchant."""
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


# ---------------------------------------------------------------------------
# Setup — matches the existing pattern used by all other cogs in the repo
# ---------------------------------------------------------------------------

def setup(bot: commands.Bot, recipe_book, guild_ids: list[int]):
    bot.add_cog(ShopCog(bot, recipe_book, guild_ids))
