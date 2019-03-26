from core.base_handler import BaseHandler, arguments, authenticated
from core.exception import NotFound, ParametersError
from .model import AccountModel
from .form import AccountLoginForm


class LoginHandler(BaseHandler):

    @arguments
    def post(self, username: str = '', password: str = '', model: AccountModel = None):
        result = model.login(username, password)
        if result:
            sid = model.update_sid(result['user_id'])
            self.clear_cookie("__sid__")
            # self.set_secure_cookie('__sid__', sid)
            self.set_cookie(
                name="__sid__",
                value=sid,
                path="/",
                expires_days=30,  # 过期时间设置为1个月
            )
            self.set_header('X-Session-Id', sid)
            print("sid::::", self.get_secure_cookie("__sid__"))
            return self.finish({
                "code": 0,
                "msg": "登录成功",
                "data": result
            })

        self.finish({
            "code": 0,
            "msg": "账户名或密码错误！"
        })


class LoginOutHandler(BaseHandler):

    @authenticated
    @arguments
    def post(self, user_id: int = None, model: AccountModel = None):
        if not user_id:
            raise ParametersError("参数错误")
        model.login_out(user_id)
        self.clear_all_cookies()
        self.finish({
            "code": 0,
            "msg": "操作成功"
        })
