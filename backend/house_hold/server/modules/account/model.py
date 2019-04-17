import uuid
import time

from core.base_model import MysqlModel
from core.schema import Account, CacheData
from core.utils import row2dict


class AccountModel(MysqlModel):

    def login(self, name, password):
        account = self.session.query(Account).filter(Account.username == name).first()
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

    def add_account(self, user_id, user_name, password):
        self.session.begin()
        if user_id is None:
            account = Account(
                username=user_name,
                password=password
            )
            self.session.add(account)
        else:
            self.session.query(Account).filter(Account.user_id==user_id).update({Account.username:user_name, Account.password:password})
        self.session.commit()

    def query_account(self, user_id):
        if user_id is None:
            result = self.session.query(Account).filter(Account.user_id != 1).all()
            return [row2dict(item) for item in result] if result else ''
        else:
            account = self.session.query(Account).filter(
                Account.user_id == user_id
            ).first()
            return row2dict(account) if account else ''

    def delete_account(self, user_id):
        self.session.query(Account).filter(Account.user_id==user_id).delete()
        self.session.flush()
