import logging

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from models.pagination import PaginatedView


_GUILD_IDS: list[int] = []

_ALIGNMENT_CHOICES = {
    "N":  "N",
    "DN": "DN",
    "ON": "ON",
    "NG": "NG",
    "NE": "NE",
    "OE": "OE",
    "DE": "DE",
    "OG": "OG",
    "DG": "DG",
}


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class FactionCog(commands.Cog):
    def __init__(self, bot: commands.Bot, recipe_book):
        self.__bot = bot
        self.__recipe_book = recipe_book

    # -----------------------------------------------------------------------
    # Internal implementation — called directly by tests to bypass the
    # nextcord slash-command decorator wrapper.
    # -----------------------------------------------------------------------

    async def _faction_impl(
        self,
        interaction: Interaction,
        player_alignment: str,
        faction_name_1: str,
        faction_alignment_1: str,
        faction_name_2: str | None = None,
        faction_alignment_2: str | None = None,
        faction_name_3: str | None = None,
        faction_alignment_3: str | None = None,
        faction_name_4: str | None = None,
        faction_alignment_4: str | None = None,
    ):
        await interaction.response.defer(ephemeral=True)

        optional_pairs = [
            (faction_name_2, faction_alignment_2, 2),
            (faction_name_3, faction_alignment_3, 3),
            (faction_name_4, faction_alignment_4, 4),
        ]
        for name, alignment, number in optional_pairs:
            if bool(name) != bool(alignment):
                await interaction.followup.send(
                    f"Faction {number}: please provide both a name **and** an alignment, or leave both blank.",
                    ephemeral=True,
                )
                return

        pairs = [
            (faction_name_1, faction_alignment_1),
            (faction_name_2, faction_alignment_2),
            (faction_name_3, faction_alignment_3),
            (faction_name_4, faction_alignment_4),
        ]

        try:
            pages = self.__recipe_book.build_faction_table.build_faction_embeds(
                player_alignment=player_alignment,
                factions=pairs,
            )
        except ValueError as e:
            await interaction.followup.send(str(e), ephemeral=True)
            return
        except Exception as exc:
            logging.error(f"/faction error: {exc}", exc_info=True)
            await interaction.followup.send(
                "Something went wrong. Please try again.", ephemeral=True
            )
            return

        if len(pages) == 1:
            await interaction.followup.send(embed=pages[0], ephemeral=True)
        else:
            view = PaginatedView(pages)
            await interaction.followup.send(
                embed=view.current_embed(), view=view, ephemeral=True
            )

    # -----------------------------------------------------------------------
    # Slash command — thin wrapper that delegates to _faction_impl
    # -----------------------------------------------------------------------

    @nextcord.slash_command(
        name="faction",
        description="Calculate NPC faction reaction(s) based on player and faction alignments.",
        guild_ids=_GUILD_IDS,
    )
    async def faction(
        self,
        interaction: Interaction,
        player_alignment: str = SlashOption(
            name="player_alignment",
            description="Your character's alignment.",
            required=True,
            choices=_ALIGNMENT_CHOICES,
        ),
        faction_name_1: str = SlashOption(
            name="faction_1_name",
            description="Name of the first faction.",
            required=True,
        ),
        faction_alignment_1: str = SlashOption(
            name="faction_1_alignment",
            description="Alignment of the first faction.",
            required=True,
            choices=_ALIGNMENT_CHOICES,
        ),
        faction_name_2: str = SlashOption(
            name="faction_2_name",
            description="Name of the second faction (optional).",
            required=False,
            default=None,
        ),
        faction_alignment_2: str = SlashOption(
            name="faction_2_alignment",
            description="Alignment of the second faction (optional).",
            required=False,
            default=None,
            choices=_ALIGNMENT_CHOICES,
        ),
        faction_name_3: str = SlashOption(
            name="faction_3_name",
            description="Name of the third faction (optional).",
            required=False,
            default=None,
        ),
        faction_alignment_3: str = SlashOption(
            name="faction_3_alignment",
            description="Alignment of the third faction (optional).",
            required=False,
            default=None,
            choices=_ALIGNMENT_CHOICES,
        ),
        faction_name_4: str = SlashOption(
            name="faction_4_name",
            description="Name of the fourth faction (optional).",
            required=False,
            default=None,
        ),
        faction_alignment_4: str = SlashOption(
            name="faction_4_alignment",
            description="Alignment of the fourth faction (optional).",
            required=False,
            default=None,
            choices=_ALIGNMENT_CHOICES,
        ),
    ):
        await self._faction_impl(
            interaction,
            player_alignment=player_alignment,
            faction_name_1=faction_name_1,
            faction_alignment_1=faction_alignment_1,
            faction_name_2=faction_name_2,
            faction_alignment_2=faction_alignment_2,
            faction_name_3=faction_name_3,
            faction_alignment_3=faction_alignment_3,
            faction_name_4=faction_name_4,
            faction_alignment_4=faction_alignment_4,
        )


def setup(bot: commands.Bot, recipe_book, guild_ids: list[int]):
    global _GUILD_IDS
    _GUILD_IDS.extend(guild_ids)
    bot.add_cog(FactionCog(bot, recipe_book))