import uuid
import time

from core.base_model import MysqlModel
from core.schema import Account, CacheData
from core.utils import row2dict, hash_password, check_password


class AccountModel(MysqlModel):

    def login(self, name, password):
        account = self.session.query(Account).filter(Account.name == name).first()
        if not account:
            return False
        else:
            account = row2dict(account)
            if account['password'] == password:
            # if check_password(account['password'], hash_password(password)):
                del account['password']
                return account
        return False

    def update_sid(self, user_id):
        session_id = str(uuid.uuid4())
        month = 60 * 60 * 24 * 30
        user = self.session.query(CacheData).filter(CacheData.user_id == user_id).first()
        if user:
            self.session.query(CacheData).filter(CacheData.user_id == user_id).update({
                CacheData.sid: session_id,
                CacheData.deadline: int(time.time()) + month
            }, synchronize_session=False)
            self.session.flush()
        else:
            self.session.begin()
            account = CacheData(
                user_id=user_id,
                sid=session_id,
                deadline=int(time.time()) + month
            )
            self.session.add(account)
            self.session.commit()
        return session_id

    def login_out(self, user_id):
        self.session.query(CacheData).filter(CacheData.user_id == user_id).delete()
        self.session.flush()


