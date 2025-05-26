from models.user import Character, DiscordAccount, Player, Name, User


class UserMapper:
    def __init__(self, database_result):
        self.database_result = database_result

    def map_to_player(self):
        return Player(
            name=Name(
                first=self.database_result["player"]["name"]["first"],
                last=self.database_result["player"]["name"]["last"],
            ),
            is_gm=self.database_result["player"]["gm"]
        )

    def map_to_character(self, is_gm):
        if is_gm:
            return None
        else:
            return Character(
                name=Name(
                    first=self.database_result["character"]["name"]["first"],
                    last=self.database_result["character"]["name"]["last"],
                ),
                level=self.database_result["character"]["level"],
                race_name=self.database_result["character"]["race"],
                class_name=self.database_result["character"]["class"],
                alignment=self.database_result["character"]["alignment"]
            )

    def map_to_discord_account(self, user_id):
        return DiscordAccount(
            user_id=user_id,
            username=self.database_result["discord"]["username"]
        )

    def map_to_user(self):
        user_id = self.database_result["userId"]
        player = self.map_to_player()
        character = self.map_to_character(player.is_gm)
        discord_account = self.map_to_discord_account(user_id)

        return User(
            player=player,
            character=character,
            discord_account=discord_account
        )