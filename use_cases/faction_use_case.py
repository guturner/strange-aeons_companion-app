def _opposite_alignment_letter(alignment_letter):
    match alignment_letter.upper():
        case "D":
            return "O"
        case "O":
            return "D"
        case "E":
            return "G"
        case "G":
            return "E"
    return "N"

def _is_one_step_from_neutral(alignment_letter):
    return alignment_letter.upper() in ["D", "O", "E", "G"]

class FactionUseCase:
    def __init__(self):
        self.__allowed_alignments = ["n", "dn", "on", "ng", "ne", "oe", "de", "og", "dg"]

    def validate_alignment(self, alignment_user_input):
        return alignment_user_input.lower() in self.__allowed_alignments

    def parse_faction_pairs(self, faction_pairs_user_input_tokens):
        """
        Given a list of user input tokens, parse them into (faction_name, faction_alignment) pairs.

        Example single-word input tokens:
            ["Bruisers", "NE", "Armada", "OG"]

        Example quoted input:
            ['"The Thieves Guild"', "DE", '"The Guards"', "NG"]
        """
        if len(faction_pairs_user_input_tokens) % 2 != 0:
            raise ValueError("You must provide faction data in faction name/faction alignment pairs.")

        faction_pairs = ()
        for i in range(0, len(faction_pairs_user_input_tokens), 2):
            faction_name = faction_pairs_user_input_tokens[i]
            faction_alignment = faction_pairs_user_input_tokens[i + 1]
            if not self.validate_alignment(faction_alignment):
                raise ValueError(f"You must provide valid faction alignments, '{faction_alignment}' is invalid.")

            faction_pairs = faction_pairs + ((faction_name.title(), faction_alignment.upper()),)

        return faction_pairs

    def calculate_faction_reaction(self, player_alignment, faction_pair):
        """
        Calculates faction reaction based on the rules here: https://strange-aeons.info/doku.php?id=ttrpg:gameplay:faction

        :param player_alignment: A one- or two-character alignment ("N", "DN", "OE", etc.)
        :param faction_pair: A tuple of (faction_name, faction_alignment) pairs
        :return: A tuple of (comparison, reaction), like: ("Completely Opposed", "Ready to Attack (-10)")
        """
        player_alignment_pair = ("N", "N") if player_alignment.upper() == "N" else (player_alignment.upper()[0], player_alignment.upper()[1])
        faction_alignment_pair = ("N", "N") if faction_pair[1].upper() == "N" else (faction_pair[1].upper()[0], faction_pair[1].upper()[1])

        if player_alignment_pair == faction_alignment_pair:
            return "Same", "Kind (+2)"

        if player_alignment_pair[0] == _opposite_alignment_letter(faction_alignment_pair[0]) and player_alignment_pair[1] == _opposite_alignment_letter(faction_alignment_pair[1]):
            return "Completely Opposed", "Ready to Attack (-10)"

        if player_alignment_pair[1] == _opposite_alignment_letter(faction_alignment_pair[1]):
            return "Opposed Good/Evil", "Threatening (-6)"

        if player_alignment_pair[1] == faction_alignment_pair[1] and player_alignment_pair[0] == _opposite_alignment_letter(faction_alignment_pair[0]):
            return "Opposed Order/Discord", "Amiable (+1)"

        if player_alignment_pair == ("N", "N") and faction_alignment_pair in [("O", "G"), ("D", "G"), ("O", "E"), ("D", "E")] or faction_alignment_pair == ("N", "N") and player_alignment_pair in [("O", "G"), ("D", "G"), ("O", "E"), ("D", "E")]:
            return "Dissimilar", "Dubious (-4)"

        return "One Step Removed", "Indifferent (+0)"