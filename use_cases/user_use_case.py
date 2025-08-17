import copy


class UserUseCase:
    def __init__(self, user_dao):
        self.__user_dao = user_dao

    # This function will attempt to upsert the User's user_id if it's null.
    def lookup_user(self, user_id=None, username=None):
        if username is not None:
            current_user = self.lookup_user_by_username(username)
            if current_user is not None and current_user.user_id is None and current_user.discord_username is not None:
                updated_user = copy.copy(current_user)
                updated_user.user_id = user_id
                return self.update_user_by_username(username, updated_user), True

        if user_id is not None:
            return self.lookup_user_by_user_id(user_id), False
        else:
            return None, False



    def lookup_user_by_user_id(self, user_id):
        return self.__user_dao.get_user_by_user_id(user_id)

    def lookup_user_by_username(self, username):
        return self.__user_dao.get_user_by_username(username)

    def update_user_by_username(self, username, new_user):
        current_user = self.lookup_user_by_username(username)
        if current_user is not None:
            return self.__user_dao.update_user_by_username(username, new_user)
        else:
            return None