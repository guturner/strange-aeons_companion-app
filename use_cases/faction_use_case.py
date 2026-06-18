import re


# ---------------------------------------------------------------------------
# Private alignment helpers
# ---------------------------------------------------------------------------

def _opposite_alignment_letter(letter: str) -> str:
    """Returns the axis-opposite of a single alignment letter.

    D ↔ O  (Discord ↔ Order)
    E ↔ G  (Evil ↔ Good)
    N → N  (Neutral has no opposite)
    """
    match letter.upper():
        case "D": return "O"
        case "O": return "D"
        case "E": return "G"
        case "G": return "E"
    return "N"


def _to_alignment_pair(alignment: str) -> tuple[str, str]:
    """Normalises an alignment code to a (order_axis, good_axis) pair.

    "N"  → ("N", "N")
    "NG" → ("N", "G")
    "DE" → ("D", "E")
    """
    a = alignment.upper()
    if a == "N":
        return ("N", "N")
    return (a[0], a[1])


def _capitalize_faction_name(name: str) -> str:
    """Title-cases a faction name, preserving apostrophe handling.

    - First letter of every word is capitalised.
    - ``'s`` possessive suffixes are left lower-case (e.g. "Faydark's Champions").
    - Other post-apostrophe letters are capitalised (e.g. "Ry'Gorr").
    """
    def _cap_word(match: re.Match) -> str:
        w = list(match.group(0).lower())
        w[0] = w[0].upper()
        for i, ch in enumerate(w):
            if ch == "'" and i + 1 < len(w):
                is_possessive_s = w[i + 1] == "s" and i + 2 == len(w)
                if not is_possessive_s:
                    w[i + 1] = w[i + 1].upper()
        return "".join(w)

    return re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*").sub(_cap_word, name)


# ---------------------------------------------------------------------------
# FactionUseCase
# ---------------------------------------------------------------------------

_ALLOWED_ALIGNMENTS = frozenset(["n", "dn", "on", "ng", "ne", "oe", "de", "og", "dg"])

# Fully-opposed diagonal pairs on the 3×3 alignment grid.
_FULLY_OPPOSED = frozenset([
    (("D", "N"), ("O", "N")),
    (("O", "N"), ("D", "N")),
    (("N", "G"), ("N", "E")),
    (("N", "E"), ("N", "G")),
    (("O", "G"), ("D", "E")),
    (("D", "E"), ("O", "G")),
    (("O", "E"), ("D", "G")),
    (("D", "G"), ("O", "E")),
])

# Alignments considered "extreme" (two axes away from N) for the Dissimilar check.
_EXTREME_ALIGNMENTS = frozenset([("O", "G"), ("D", "G"), ("O", "E"), ("D", "E")])


class FactionUseCase:
    """
    Domain logic for faction alignment reactions.

    Reaction rules: https://strange-aeons.info/doku.php?id=ttrpg:gameplay:faction

    This class owns:
      - alignment validation
      - faction name normalisation
      - reaction calculation

    It does NOT own text parsing (that belonged to the old prefix-command path,
    which has been removed now that /faction is a slash command with structured
    inputs).
    """

    def validate_alignment(self, alignment: str) -> bool:
        """Returns True if *alignment* is a legal alignment code."""
        return alignment.lower() in _ALLOWED_ALIGNMENTS

    def normalize_faction_name(self, name: str) -> str:
        """Applies consistent title-casing to a faction name."""
        return _capitalize_faction_name(name)

    def calculate_faction_reaction(
        self,
        player_alignment: str,
        faction_pair: tuple[str, str],
    ) -> tuple[str, str]:
        """
        Returns ``(comparison_label, reaction_label)`` describing how a faction
        with *faction_pair[1]* reacts to a player whose alignment is
        *player_alignment*.

        :param player_alignment: One- or two-character code ("N", "NG", "DE", …).
        :param faction_pair: ``(faction_name, faction_alignment)`` tuple.
                             Only ``faction_pair[1]`` (the alignment) is used.
        :returns: e.g. ``("Completely Opposed", "Ready to Attack (-10)")``

        Reaction priority (highest wins):
          1. Same               → Kind (+2)
          2. Completely Opposed → Ready to Attack (-10)
          3. Opposed Good/Evil  → Threatening (-6)
          4. Opposed Order/Discord → Amiable (+1)
          5. Dissimilar         → Dubious (-4)   [N vs extreme, or extreme vs N]
          6. One Step Removed   → Indifferent (+0)
        """
        pp = _to_alignment_pair(player_alignment)
        fp = _to_alignment_pair(faction_pair[1])

        if pp == fp:
            return "Same", "Kind (+2)"

        if (_opposite_alignment_letter(pp[0]) == fp[0]
                and _opposite_alignment_letter(pp[1]) == fp[1]):
            return "Completely Opposed", "Ready to Attack (-10)"

        if _opposite_alignment_letter(pp[1]) == fp[1]:
            return "Opposed Good/Evil", "Threatening (-6)"

        if pp[1] == fp[1] and _opposite_alignment_letter(pp[0]) == fp[0]:
            return "Opposed Order/Discord", "Amiable (+1)"

        if (pp == ("N", "N") and fp in _EXTREME_ALIGNMENTS
                or fp == ("N", "N") and pp in _EXTREME_ALIGNMENTS):
            return "Dissimilar", "Dubious (-4)"

        return "One Step Removed", "Indifferent (+0)"