from results import LookupUserFailure, LookupUserSuccess


class LookupUserUseCase:
    def __init__(self, user_dao):
        self.__user_dao = user_dao

    def lookup_user_by_user_id(self, user_id):
        user = self.__user_dao.get_user_by_user_id(user_id)
        if user is not None:
            return LookupUserSuccess(user)

        return LookupUserFailure(user_id=user_id, username=None)

    def lookup_user_by_username(self, username):
        user = self.__user_dao.get_user_by_username(username)
        if user is not None:
            return LookupUserSuccess(user)

        return LookupUserFailure(user_id=None, username=username)