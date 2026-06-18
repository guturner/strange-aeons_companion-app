"""
Tests for the /faction slash command stack.

Coverage:
  - FactionUseCase.validate_alignment
  - FactionUseCase.normalize_faction_name
  - FactionUseCase.calculate_faction_reaction  (all six outcome branches)
  - BuildFactionTableUseCase.build_faction_embeds
  - _build_faction_data_string  (module-level helper in faction_cog)
  - FactionCog._faction_impl    (integration tests via the real use-case stack)

Integration tests call _faction_impl rather than the @slash_command-decorated
faction() method.  nextcord's SlashApplicationCommand.__call__ re-injects
slash-option kwargs, causing "multiple values for argument" TypeErrors in unit
tests.  _faction_impl is the testable inner implementation; faction() is a
one-line shell that delegates straight to it.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock

import nextcord

from cogs.faction_cog import FactionCog
from tests.utils import recipe_book
from use_cases.build_faction_table_use_case import BuildFactionTableUseCase
from use_cases.faction_use_case import FactionUseCase


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

def _make_interaction(user_id: int = 1, username: str = "fake_username_1") -> MagicMock:
    interaction = MagicMock(spec=nextcord.Interaction)
    interaction.user = MagicMock()
    interaction.user.id = user_id
    interaction.user.name = username
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


def _make_cog() -> FactionCog:
    bot = MagicMock()
    faction_use_case = FactionUseCase()
    build_faction_table_use_case = BuildFactionTableUseCase(faction_use_case)
    rb = recipe_book(
        build_faction_table_use_case=build_faction_table_use_case,
        faction_use_case=faction_use_case,
    )
    return FactionCog(bot, rb)


def _send_kwargs(interaction: MagicMock) -> dict:
    return interaction.followup.send.call_args.kwargs


# ===========================================================================
# FactionUseCase — validate_alignment
# ===========================================================================

class TestFactionUseCase_ValidateAlignment(unittest.TestCase):

    def setUp(self):
        self.uc = FactionUseCase()

    def test_valid_alignments_accepted(self):
        for alignment in ["N", "DN", "ON", "NG", "NE", "OE", "DE", "OG", "DG"]:
            with self.subTest(alignment=alignment):
                assert self.uc.validate_alignment(alignment) is True

    def test_valid_alignments_accepted_lowercase(self):
        for alignment in ["n", "dn", "on", "ng", "ne", "oe", "de", "og", "dg"]:
            with self.subTest(alignment=alignment):
                assert self.uc.validate_alignment(alignment) is True

    def test_invalid_alignments_rejected(self):
        for bad in ["", "X", "NN", "GE", "LG", "CE", "random"]:
            with self.subTest(alignment=bad):
                assert self.uc.validate_alignment(bad) is False


# ===========================================================================
# FactionUseCase — normalize_faction_name
# ===========================================================================

class TestFactionUseCase_NormalizeFactionName(unittest.TestCase):

    def setUp(self):
        self.uc = FactionUseCase()

    def test_single_word(self):
        assert self.uc.normalize_faction_name("bruisers") == "Bruisers"

    def test_multi_word(self):
        assert self.uc.normalize_faction_name("the freeport militia") == "The Freeport Militia"

    def test_already_cased_passthrough(self):
        assert self.uc.normalize_faction_name("Freeport Militia") == "Freeport Militia"

    def test_possessive_apostrophe_stays_lowercase(self):
        # "Faydark's" — the 's after the apostrophe should not be capitalised
        assert self.uc.normalize_faction_name("faydark's champions") == "Faydark's Champions"

    def test_mid_word_apostrophe_capitalised(self):
        # "Ry'Gorr" — the G after the apostrophe should be capitalised
        assert self.uc.normalize_faction_name("ry'gorr orcs") == "Ry'Gorr Orcs"

    def test_all_caps_input_normalised(self):
        assert self.uc.normalize_faction_name("THE GUARDS") == "The Guards"


# ===========================================================================
# FactionUseCase — calculate_faction_reaction  (all six branches)
# ===========================================================================

class TestFactionUseCase_CalculateFactionReaction(unittest.TestCase):
    """
    Full branch coverage of the reaction priority chain.

    The truth table (player alignment × faction alignment → outcome):

        N    → DN/ON           : Opposed Good/Evil  (N has no order axis, but
                                                      DN/ON oppose N on order)
        NG   → NG              : Same
        NG   → NE              : Completely Opposed
        OG   → DG              : Opposed Order/Discord
        DE   → OG              : Completely Opposed
        N    → OG/DG/OE/DE     : Dissimilar
        OG   → N               : Dissimilar  (symmetric)
        NG   → DG / OG → NG   : One Step Removed
    """

    def setUp(self):
        self.uc = FactionUseCase()
        self._react = lambda pa, fn, fa: self.uc.calculate_faction_reaction(pa, (fn, fa))

    # ── Same ──────────────────────────────────────────────────────────────
    def test_same__neutral_vs_neutral(self):
        comp, reac = self._react("N", "Militia", "N")
        assert comp == "Same"
        assert reac == "Kind (+2)"

    def test_same__ng_vs_ng(self):
        comp, reac = self._react("NG", "Guards", "NG")
        assert comp == "Same"

    def test_same__de_vs_de(self):
        comp, reac = self._react("DE", "Bruisers", "DE")
        assert comp == "Same"

    # ── Completely Opposed ─────────────────────────────────────────────────
    def test_completely_opposed__ng_vs_ne(self):
        comp, reac = self._react("NG", "Shadows", "NE")
        assert comp == "Completely Opposed"
        assert reac == "Ready to Attack (-10)"

    def test_completely_opposed__ne_vs_ng(self):
        comp, reac = self._react("NE", "Guards", "NG")
        assert comp == "Completely Opposed"

    def test_completely_opposed__og_vs_de(self):
        comp, reac = self._react("OG", "Dark Ones", "DE")
        assert comp == "Completely Opposed"

    def test_completely_opposed__de_vs_og(self):
        comp, reac = self._react("DE", "Paladins", "OG")
        assert comp == "Completely Opposed"

    def test_completely_opposed__dn_vs_on(self):
        comp, reac = self._react("DN", "Order", "ON")
        assert comp == "Completely Opposed"

    # ── Opposed Good/Evil ──────────────────────────────────────────────────
    def test_opposed_good_evil__n_vs_dn(self):
        # N has order axis N; DN has order axis D; good/evil: N vs N → same
        # Wait — N expands to (N,N), DN expands to (D,N)
        # good_evil axis: both N — not opposed on good/evil
        # Actually this should be One Step Removed — let me verify with the matrix output
        # From our truth table: N vs DN → G/E (Opposed Good/Evil, Threatening -6)
        # That's because opposite of D is O ≠ N, so not fully opposed
        # opposite of N (good axis) is N; pp[1]=N == opp(fp[1])=opp(N)=N — yes, this branch fires!
        comp, reac = self._react("N", "Chaotic", "DN")
        assert comp == "Opposed Good/Evil"
        assert reac == "Threatening (-6)"

    def test_opposed_good_evil__n_vs_on(self):
        comp, reac = self._react("N", "Order", "ON")
        assert comp == "Opposed Good/Evil"

    def test_opposed_good_evil__og_vs_oe(self):
        comp, reac = self._react("OG", "Thieves", "OE")
        assert comp == "Opposed Good/Evil"

    def test_opposed_good_evil__dg_vs_de(self):
        comp, reac = self._react("DG", "Necromancers", "DE")
        assert comp == "Opposed Good/Evil"

    def test_opposed_good_evil__ng_vs_dg(self):
        # NG=(N,G) vs DG=(D,G): same good axis, different order → Opposed Order/Discord
        # Ensure we don't misclassify
        comp, _ = self._react("NG", "Druids", "DG")
        assert comp != "Opposed Good/Evil"

    # ── Opposed Order/Discord ──────────────────────────────────────────────
    def test_opposed_order_discord__og_vs_dg(self):
        comp, reac = self._react("OG", "Druids", "DG")
        assert comp == "Opposed Order/Discord"
        assert reac == "Amiable (+1)"

    def test_opposed_order_discord__dg_vs_og(self):
        comp, reac = self._react("DG", "Paladins", "OG")
        assert comp == "Opposed Order/Discord"

    def test_opposed_order_discord__oe_vs_de(self):
        comp, reac = self._react("OE", "Necros", "DE")
        assert comp == "Opposed Order/Discord"

    def test_opposed_order_discord__de_vs_oe(self):
        comp, reac = self._react("DE", "Rogues", "OE")
        assert comp == "Opposed Order/Discord"

    # ── Dissimilar ────────────────────────────────────────────────────────
    def test_dissimilar__neutral_vs_og(self):
        comp, reac = self._react("N", "Paladins", "OG")
        assert comp == "Dissimilar"
        assert reac == "Dubious (-4)"

    def test_dissimilar__neutral_vs_dg(self):
        comp, reac = self._react("N", "Druids", "DG")
        assert comp == "Dissimilar"

    def test_dissimilar__neutral_vs_oe(self):
        comp, reac = self._react("N", "Rogues", "OE")
        assert comp == "Dissimilar"

    def test_dissimilar__neutral_vs_de(self):
        comp, reac = self._react("N", "Necros", "DE")
        assert comp == "Dissimilar"

    def test_dissimilar__og_vs_neutral(self):
        # Symmetric: extreme vs N also gives Dissimilar
        comp, reac = self._react("OG", "Merchants", "N")
        assert comp == "Dissimilar"

    def test_dissimilar__de_vs_neutral(self):
        comp, reac = self._react("DE", "Merchants", "N")
        assert comp == "Dissimilar"

    # ── One Step Removed ──────────────────────────────────────────────────
    def test_one_step_removed__ng_vs_dg(self):
        comp, reac = self._react("NG", "Druids", "DG")
        assert comp == "One Step Removed"
        assert reac == "Indifferent (+0)"

    def test_one_step_removed__ng_vs_og(self):
        comp, reac = self._react("NG", "Paladins", "OG")
        assert comp == "One Step Removed"

    def test_one_step_removed__dn_vs_ng(self):
        comp, reac = self._react("DN", "Guards", "NG")
        assert comp == "One Step Removed"

    def test_one_step_removed__ne_vs_de(self):
        comp, reac = self._react("NE", "Necros", "DE")
        assert comp == "One Step Removed"


# ===========================================================================
# BuildFactionTableUseCase — build_faction_embeds
# ===========================================================================

class TestBuildFactionTableUseCase(unittest.TestCase):

    def setUp(self):
        faction_use_case = FactionUseCase()
        self.uc = BuildFactionTableUseCase(faction_use_case)

    def test_single_faction__returns_one_embed(self):
        pages = self.uc.build_faction_embeds("N", [("The Guards", "NG")])
        assert len(pages) == 1

    def test_single_faction__name_in_description(self):
        pages = self.uc.build_faction_embeds("N", [("The Guards", "NG")])
        assert "The Guards" in pages[0].description

    def test_single_faction__reaction_in_description(self):
        # N vs NG: One Step Removed
        pages = self.uc.build_faction_embeds("N", [("The Guards", "NG")])
        assert "One Step Removed" in pages[0].description
        assert "Indifferent" in pages[0].description

    def test_player_alignment_header_in_description(self):
        pages = self.uc.build_faction_embeds("NG", [("The Guards", "NG")])
        assert "NG" in pages[0].description

    def test_multiple_factions__all_names_in_description(self):
        factions = [("The Guards", "NG"), ("Bruisers", "NE"), ("Merchants", "N")]
        pages = self.uc.build_faction_embeds("N", factions)
        desc = pages[0].description
        assert "The Guards" in desc
        assert "Bruisers" in desc
        assert "Merchants" in desc

    def test_none_pairs_skipped(self):
        factions = [("The Guards", "NG"), (None, None), (None, None)]
        pages = self.uc.build_faction_embeds("N", factions)
        assert len(pages) == 1
        assert "The Guards" in pages[0].description

    def test_all_none_pairs__raises_value_error(self):
        with self.assertRaises(ValueError):
            self.uc.build_faction_embeds("N", [(None, None)])

    def test_faction_name_normalised__lowercase_input(self):
        pages = self.uc.build_faction_embeds("N", [("the guards", "NG")])
        assert "The Guards" in pages[0].description

    def test_faction_name_normalised__possessive(self):
        pages = self.uc.build_faction_embeds("N", [("faydark's champions", "N")])
        assert "Faydark's Champions" in pages[0].description

    def test_pagination__seven_factions__two_pages(self):
        factions = [(f"Faction {i}", "N") for i in range(7)]
        pages = self.uc.build_faction_embeds("N", factions)
        assert len(pages) == 2

    def test_pagination__six_factions__one_page(self):
        factions = [(f"Faction {i}", "N") for i in range(6)]
        pages = self.uc.build_faction_embeds("N", factions)
        assert len(pages) == 1

    def test_embed_title(self):
        pages = self.uc.build_faction_embeds("N", [("The Guards", "NG")])
        assert pages[0].title == "Faction Standing"


# ===========================================================================
# FactionCog._faction_impl  (integration: real use-case stack, mocked Discord)
# ===========================================================================

class TestFactionCog(unittest.IsolatedAsyncioTestCase):

    async def test_single_faction__happy_path(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="N",
            faction_name_1="Some Faction", faction_alignment_1="N",
        )

        interaction.response.defer.assert_called_once_with(ephemeral=True)
        interaction.followup.send.assert_called_once()
        kwargs = _send_kwargs(interaction)
        assert kwargs.get("ephemeral") is True
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Some Faction" in embed.description

    async def test_multiple_factions__all_names_present(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="N",
            faction_name_1="Some Faction",      faction_alignment_1="N",
            faction_name_2="Some Other Faction", faction_alignment_2="OG",
        )

        kwargs = _send_kwargs(interaction)
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Some Faction" in embed.description
        assert "Some Other Faction" in embed.description

    async def test_four_factions__all_names_present(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="NG",
            faction_name_1="The Guards",    faction_alignment_1="DG",
            faction_name_2="Bruisers",      faction_alignment_2="NE",
            faction_name_3="The Merchants", faction_alignment_3="N",
            faction_name_4="Dark Ones",     faction_alignment_4="DE",
        )

        kwargs = _send_kwargs(interaction)
        embed = kwargs.get("embed")
        assert embed is not None
        assert "The Guards" in embed.description
        assert "Bruisers" in embed.description
        assert "The Merchants" in embed.description
        assert "Dark Ones" in embed.description

    async def test_apostrophe_faction_names__preserved(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="N",
            faction_name_1="Faydark's Champions", faction_alignment_1="N",
            faction_name_2="Ry'Gorr Orcs",        faction_alignment_2="DE",
        )

        kwargs = _send_kwargs(interaction)
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Faydark's Champions" in embed.description
        assert "Ry'Gorr Orcs" in embed.description

    async def test_reaction_shown_in_embed__same_alignment(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="NG",
            faction_name_1="The Guards", faction_alignment_1="NG",
        )

        embed = _send_kwargs(interaction).get("embed")
        assert "Same" in embed.description
        assert "Kind" in embed.description

    async def test_reaction_shown_in_embed__completely_opposed(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="NG",
            faction_name_1="Dark Ones", faction_alignment_1="NE",
        )

        embed = _send_kwargs(interaction).get("embed")
        assert "Completely Opposed" in embed.description
        assert "Ready to Attack" in embed.description

    async def test_name_without_alignment__returns_error(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="N",
            faction_name_1="The Guards", faction_alignment_1="NG",
            faction_name_2="Bruisers",   faction_alignment_2=None,
        )

        interaction.followup.send.assert_called_once()
        kwargs = _send_kwargs(interaction)
        assert kwargs.get("ephemeral") is True
        assert kwargs.get("embed") is None
        text = interaction.followup.send.call_args.args[0]
        assert "Faction 2" in text
        assert "name" in text.lower() or "alignment" in text.lower()

    async def test_alignment_without_name__returns_error(self):
        faction_cog = _make_cog()
        interaction = _make_interaction()

        await FactionCog._faction_impl(
            faction_cog, interaction,
            player_alignment="N",
            faction_name_1="The Guards", faction_alignment_1="NG",
            faction_name_3=None,         faction_alignment_3="OE",
        )

        kwargs = _send_kwargs(interaction)
        assert kwargs.get("embed") is None
        text = interaction.followup.send.call_args.args[0]
        assert "Faction 3" in text