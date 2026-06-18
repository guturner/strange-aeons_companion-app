import nextcord

_EMBED_COLOR = 0xC8A96E
_FACTIONS_PER_PAGE = 6

_FACTION_ICON = "🏳️"

# Maps comparison label → emoji for quick visual scanning in Discord
_REACTION_ICONS = {
    "Same":                  "💚",
    "Opposed Order/Discord": "🟡",
    "One Step Removed":      "🟡",
    "Dissimilar":            "🟠",
    "Opposed Good/Evil":     "🔴",
    "Completely Opposed":    "💀",
}


def _faction_entry(faction_name: str, faction_alignment: str, comparison: str, reaction: str) -> str:
    """
    Formats a single faction result as a two-line Discord markdown string.

    Example:
        🏳️  **Freeport Militia** (NG)
        💚  Same → Kind (+2)
    """
    icon = _REACTION_ICONS.get(comparison, "❓")
    return (
        f"{_FACTION_ICON}  **{faction_name}** ({faction_alignment})\n"
        f"{icon}  {comparison} → {reaction}"
    )


class BuildFactionTableUseCase:
    """
    Builds paginated Discord embeds for the /faction slash command.

    Depends on FactionUseCase for:
      - faction name normalisation (title-casing)
      - reaction calculation
    """

    def __init__(self, faction_use_case):
        self.__faction_use_case = faction_use_case

    def build_faction_embeds(
        self,
        player_alignment: str,
        factions: list[tuple[str | None, str | None]],
    ) -> list[nextcord.Embed]:
        """
        Returns one embed per page (up to ``_FACTIONS_PER_PAGE`` factions each).

        All faction content lives in ``embed.description`` so names are easily
        searchable in tests and the layout is consistent with other bot embeds.
        ``None`` pairs are silently skipped.

        :param player_alignment: The player's alignment code ("N", "NG", "DE", …).
        :param factions: List of ``(faction_name, faction_alignment)`` tuples.
        :returns: Non-empty list of ``nextcord.Embed`` objects.
        :raises ValueError: If no valid (non-None) factions are provided.
        """
        active = [
            (self.__faction_use_case.normalize_faction_name(name), alignment)
            for name, alignment in factions
            if name is not None and alignment is not None
        ]

        if not active:
            raise ValueError("No factions provided.")

        pages: list[nextcord.Embed] = []

        for page_start in range(0, len(active), _FACTIONS_PER_PAGE):
            chunk = active[page_start: page_start + _FACTIONS_PER_PAGE]

            entries: list[str] = []
            for faction_name, faction_alignment in chunk:
                comparison, reaction = self.__faction_use_case.calculate_faction_reaction(
                    player_alignment, (faction_name, faction_alignment)
                )
                entries.append(_faction_entry(faction_name, faction_alignment, comparison, reaction))

            description = (
                f"-# Your alignment: **{player_alignment.upper()}**\n\n"
                + "\n\n".join(entries)
            )

            embed = nextcord.Embed(
                title="Faction Standing",
                description=description,
                color=_EMBED_COLOR,
            )

            pages.append(embed)

        return pages