from results import LookupUserSuccess, UpdateUserFailure, UpdateUserSuccess


class UpdateUserUseCase:
    def __init__(self, lookup_user_use_case, user_dao):
        self.__lookup_user_use_case = lookup_user_use_case
        self.__user_dao = user_dao

    def update_user_by_username(self, username, new_user):
        lookup_user_result = self.__lookup_user_use_case.lookup_user_by_username(username)
        match lookup_user_result:
            case LookupUserSuccess():
                updated_user = self.__user_dao.update_user_by_username(username, new_user)
                return UpdateUserSuccess(updated_user)

        return UpdateUserFailure(user_id=new_user.user_id, username=username)