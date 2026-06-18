"""
Paginated embed view with Prev / Next buttons.

Usage:
    view = PaginatedView(pages)
    await interaction.followup.send(embed=view.current_embed(), view=view, ephemeral=True)
"""

import nextcord
from nextcord import Interaction


class PaginatedView(nextcord.ui.View):
    """
    Generic paginated embed navigator.

    - Prev/Next buttons are disabled when there is no further page.
    - Footer shows "Page N of M" when more than one page exists.
    - Times out after *timeout* seconds (default 180 s / 3 min).
    """

    def __init__(self, pages: list[nextcord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        if not pages:
            raise ValueError("PaginatedView requires at least one page.")
        self.pages = pages
        self.index = 0
        self._sync_buttons()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def current_embed(self) -> nextcord.Embed:
        """Returns the current page embed, with a page-number footer if paginated."""
        embed = self.pages[self.index]
        if len(self.pages) > 1:
            embed.set_footer(text=f"Page {self.index + 1} of {len(self.pages)}")
        return embed

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    @nextcord.ui.button(label="◀  Prev", style=nextcord.ButtonStyle.secondary)
    async def prev_button(self, _button: nextcord.ui.Button, interaction: Interaction):
        self.index -= 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @nextcord.ui.button(label="Next  ▶", style=nextcord.ButtonStyle.secondary)
    async def next_button(self, _button: nextcord.ui.Button, interaction: Interaction):
        self.index += 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def on_timeout(self):
        self.prev_button.disabled = True
        self.next_button.disabled = True
        self.stop()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _sync_buttons(self):
        self.prev_button.disabled = self.index == 0
        self.next_button.disabled = self.index >= len(self.pages) - 1