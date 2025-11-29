import shlex


class BuildFactionTableUseCase:
    def __init__(self, build_table_use_case, faction_use_case):
        self.__build_table_use_case = build_table_use_case
        self.__faction_use_case = faction_use_case

    def build_faction_tables(self, raw_player_alignment, raw_faction_data):
        is_player_alignment_valid = self.__faction_use_case.validate_alignment(raw_player_alignment)
        if is_player_alignment_valid:
            player_alignment = raw_player_alignment.upper()
        else:
            raise ValueError("Your player alignment should be a one- or two-character abbreviation, for example: N, DN, ON, etc.")

        user_input_tokens = shlex.split(raw_faction_data)
        faction_pairs = self.__faction_use_case.parse_faction_pairs(user_input_tokens)

        headers = ("PLAYER ALIGNMENT", "FACTION NAME", "FACTION ALIGNMENT", "ALIGNMENT COMPARISON", "FACTION REACTION")
        rows = tuple(
            (player_alignment,) + faction_pair + self.__faction_use_case.calculate_faction_reaction(player_alignment, faction_pair)
            for faction_pair in faction_pairs
        )

        raw_tables = self.__build_table_use_case.build_ascii_tables(headers, rows)
        return [f"```\n{table}```" for table in raw_tables]