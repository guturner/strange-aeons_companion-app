class User:
    def __init__(self, player, character, discord_account):
        self.user_id = discord_account.user_id
        self.player = player
        self.player_first_name = player.first_name
        self.player_last_name = player.last_name
        self.character = character
        self.character_first_name = character.first_name if character is not None else None
        self.character_last_name = character.last_name if character is not None else None
        self.character_level = character.level if character is not None else None
        self.character_race = character.race if character is not None else None
        self.character_class = character.cls if character is not None else None
        self.discord_username = discord_account.username
        self.is_gm = player.is_gm

class Player:
    def __init__(self, name, is_gm):
        self.first_name = name.first
        self.last_name = name.last
        self.is_gm = is_gm

class Character:
    def __init__(self, name, level, race_name, class_name, alignment):
        self.first_name = name.first
        self.last_name = name.last or ""
        self.level = level
        self.race = race_name
        self.cls = class_name
        self.alignment = alignment

class DiscordAccount:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

class Name:
    def __init__(self, first, last):
        self.first = first
        self.last = last