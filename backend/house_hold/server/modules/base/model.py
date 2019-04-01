from core.schema import User, ObjID
from core.base_model import MysqlModel
from core.exception import NotFound, ParametersError


class TestModel(MysqlModel):
    def get_user_by_id(self, user_id: str = ''):
        if not ObjID.is_valid(user_id):
            raise ParametersError('user_id: %r is not valid'.format(user_id))
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            return user
        else:
            raise NotFound('Can not found user by id: %r'.format(user_id))


