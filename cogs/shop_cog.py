import logging

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

# ---------------------------------------------------------------------------
# Guild IDs — set by setup() before the cog class body is evaluated.
# This is the standard nextcord pattern for guild-scoped cog commands.
# ---------------------------------------------------------------------------
_GUILD_IDS: list[int] = []


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
    def __init__(self, bot: commands.Bot, recipe_book, guild_ids: list[int]):
        self.__bot = bot
        self.__recipe_book = recipe_book
        self._guild_ids = guild_ids

    # ------------------------------------------------------------------
    # Autocomplete — city dropdown filtered to cities the user occupies
    # ------------------------------------------------------------------

    async def _autocomplete_city(self, interaction: Interaction, data: str):
        discord_user_id = interaction.user.id
        cities = self.__recipe_book.build_inventory_table.lookup_cities_by_discord_user_id(discord_user_id)

        if not cities:
            await interaction.response.send_autocomplete([])
            return

        typed = data.strip().lower()
        matches = [
            city.name for city in cities
            if not typed or typed in city.name.lower()
        ]

        await interaction.response.send_autocomplete(matches[:25])

    # ------------------------------------------------------------------
    # /shop — guild_ids comes from the module-level _GUILD_IDS list,
    # which setup() populates before add_cog() is called.
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
            description="Your city (autocompletes to cities you occupy)",
            required=True,
            autocomplete=True,
        ),
        merchant_name: str = SlashOption(
            name="merchant",
            description="Name of the merchant (leave blank to list all merchants)",
            required=False,
            default=None,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        logging.info(
            f"/shop invoked by {interaction.user} (id={interaction.user.id}) "
            f"| city={city_name!r} merchant={merchant_name!r}"
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

    @shop.on_autocomplete("city_name")
    async def autocomplete_city_name(self, interaction: Interaction, data: str):
        await self._autocomplete_city(interaction, data)

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


# ---------------------------------------------------------------------------
# Setup — populate _GUILD_IDS before add_cog so the decorator picks them up.
# ShopCog no longer takes guild_ids in __init__ since the decorator reads
# the module-level list at class definition time.
# ---------------------------------------------------------------------------

def setup(bot: commands.Bot, recipe_book, guild_ids: list[int]):
    global _GUILD_IDS
    _GUILD_IDS.extend(guild_ids)
    bot.add_cog(ShopCog(bot, recipe_book, guild_ids))