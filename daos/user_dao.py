from pymongo import ReturnDocument

from daos.dao import DAO
from mappers.user_mapper import UserMapper


class UserDAO(DAO):
    def __init__(self, database):
        super().__init__(database)

    def get_user_by_user_id(self, user_id):
        result = self._db["users"].find_one({"userId": user_id})
        return UserMapper(result).map_to_user() if result else None

    def get_user_by_username(self, username):
        result = self._db["users"].find_one({"discord.username": {"$regex": f"^{username}$", "$options": "i"}})
        return UserMapper(result).map_to_user() if result else None

    def update_user_by_username(self, username, user):
        user_filter = {
            "userId": user.user_id,
        }

        player_filter = {
            "player.name.first": user.player_first_name,
            "player.name.last": user.player_last_name,
            "player.gm": user.is_gm
        }

        discord_filter = {
            "discord.username": username,
        }

        if user.character is not None:
            character_filter = {
                "character.name.first": user.character_first_name,
                "character.name.last": user.character_last_name,
                "character.level": user.character_level,
                "character.race": user.character_race,
                "character.class": user.character_class,
            }
        else:
            character_filter = None

        if character_filter is not None:
            update_filter = {
                **user_filter,
                **player_filter,
                **discord_filter,
                **character_filter
            }
        else:
            update_filter = {
                **user_filter,
                **player_filter,
                **discord_filter
            }

        result = self._db["users"].find_one_and_update(
            {
                "discord.username": username
            },
            {
                "$set": update_filter
            },
            return_document=ReturnDocument.AFTER
        )
        return UserMapper(result).map_to_user() if result else None
