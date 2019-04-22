import json
import logging
import functools
import uuid
import time
from inspect import getfullargspec, iscoroutinefunction
from tornado.gen import is_coroutine_function
from tornado.options import options
from itertools import zip_longest
from tornado.web import RequestHandler, Finish
from core.redisdb import redis_cli, pickle, stalecache
from settings.constant import SESSION_CACHE_EXPIRE
from .base_model import BaseModel, HandlerContext, MysqlModel
from .exception import (
    NotFound,
    ParametersError,
    FileTypeError,
    Duplicate,
    PermissionDenied,
    InternalError,
)
# from core.schema import CacheData


class SessionHandler(RequestHandler):

    # def get_current_user(self):
    #     """根据cookie信息从redis中获取用户身份"""
    #     session_id = self.request.headers.get('X-Session-Id') or self.get_cookie('__sid__')
    #     if session_id:
    #         return session_id
    #     return None

    def get_current_user(self):
        """根据cookie信息从redis中获取用户身份"""
        session_id = self.request.headers.get('X-Session-Id') or self.get_cookie('__sid__')
        if session_id:
            user_id = redis_cli().get('{}:sid:{}'.format(options.REDIS_NAMESPACE, session_id))
            if user_id:
                return user_id.decode()
        return None

    def gen_session_id(self, user_id=''):
        """生成session_id，存储于头部和redis"""
        expires_days = 30
        session_id = str(uuid.uuid4())
        redis_cli().pipeline().set(
            '{}:sid:{}'.format(options.REDIS_NAMESPACE, session_id), user_id or self.current_user
        ).expire(
            '{}:sid:{}'.format(options.REDIS_NAMESPACE, session_id), 3600 * 24 * expires_days
        ).execute()
        self.set_cookie(
            name="__sid__",
            value=session_id,
            path="/",
            expires_days=expires_days,  # 过期时间设置为1个月
        )
        self.set_header('X-Session-Id', session_id)
        return session_id

    @property
    def session_key(self):
        return '{user_type}:user:{user_id}'.format(
            user_type=self.request.headers.get('X-Session-Type', 'shield'),
            user_id=self.current_user,
        )

    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = self._get_user(self.current_user)
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        redis_cli().pipeline().set(
            self.session_key, pickle.dumps(value)
        ).expire(
            self.session_key, value and SESSION_CACHE_EXPIRE or 0
        ).execute()

    @stalecache(stale=0, expire=SESSION_CACHE_EXPIRE, attr_key='session_key')
    def _get_user(self, current_user):
        return self.get_user(current_user)

    def get_user(self, current_user):
        raise NotImplementedError()

    @property
    def device_id(self):
        """获取设备号（由前端生成）"""
        return self.request.headers.get("X-Device-Id", "")

    @property
    def version(self):
        """获取版本号（由前端生成）"""
        return self.request.headers.get("X-Version", "")

    def _request_summary(self):
        """请求结束后打印总结信息"""
        request_info = f"{self.request.method} {self.request.uri} ({self.request.remote_ip}) "
        request_info += f"({self.version}) ({self.device_id}) ({self.request._start_time})"
        return request_info


def authenticated(method):
    """检查是否登录"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.set_status(401, "请登录!")
            self.finish({"code": -1, "msg": "请登录!"})
            return None
        return method(self, *args, **kwargs)
    return wrapper


# def authenticated(method):
#     """检查是否登录"""
#     @functools.wraps(method)
#     def wrapper(self, *args, **kwargs):
#         if not self.current_user:
#             self.set_status(401, "请登录!")
#             self.finish({"code": -1, "msg": "请登录!"})
#             return None
#         try:
#             model = MysqlModel()
#             cache = model.session.query(CacheData).filter(CacheData.sid == self.current_user).first()
#             if not cache:
#                 self.set_status(401, "请登录!")
#                 self.finish({"code": -1, "msg": "请登录!"})
#                 return None
#             else:
#                 if int(cache.deadline) < int(time.time()):
#                     self.set_status(401, "请登录!")
#                     self.finish({"code": -1, "msg": "请登录!"})
#                     return None
#         except Exception as e:
#             logging.error("update visit time and source failed..., and error reason:%r", e)
#         return method(self, *args, **kwargs)
#     return wrapper


class JsonHandler(SessionHandler):
    """尝试从请求体中提取json"""

    def __init__(self, application, request, **kwargs):
        self._json_args = {}
        super().__init__(application, request, **kwargs)

    def set_default_headers(self):
        """设置默认头信息为json, 设置跨域方便调试"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        origin = self.request.headers.get('Origin')
        host = self.request.headers.get('Host')
        if origin and origin.split('/')[-1] != host:
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header("Access-Control-Allow-Credentials", 'true')
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            self.set_header('Access-Control-Max-Age', '1728000')
            self.set_header("Access-Control-Allow-Headers",
                            "x-requested-with, x-device-id, x-version, "
                            "content-encoding, content-length, content-type, "
                            "authorization, cache-control")

    def prepare(self):
        """尝试从请求体中提取json"""
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return
        if "multipart/form-data" in self.request.headers.get("Content-Type", ""):
            return
        try:
            body = self.request.body.decode('utf8')
            self._json_args = body and json.loads(body) or {}
        except Exception as e:
            logging.info(e)

    def options(self, *args, **kwargs):
        pass


class BaseHandler(JsonHandler):
    """所有应用层Handler使用此类"""


def arguments(method):
    """从请求体自动装填被修饰方法的参数，自动类型转换，捕获异常"""
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        spec = getfullargspec(method)
        filling_args = spec.args[len(args) + 1:]  # 切出需要填充的参数
        default_values = spec.defaults[-len(filling_args):] if spec.defaults else []  # 切出需要的默认值

        # 倒序，参数与默认值对齐
        for key, default in zip_longest(reversed(filling_args), reversed(default_values)):
            if key in kwargs:
                continue
            if key in self._json_args:
                kwargs[key] = self._json_args.get(key)
                continue
            if isinstance(default, list):
                value = self.get_arguments(key, True) or default
            else:
                value = self.get_argument(key, default)
            kwargs[key] = value

        # 根据注解做类型转换
        model_dict = {}
        for key, value in kwargs.items():
            if key not in spec.annotations:
                continue
            annotations = spec.annotations.get(key)
            try:
                if issubclass(annotations, BaseModel):
                    model = annotations(context=HandlerContext(self))
                    kwargs[key] = model
                    model_dict[key] = model
                elif isinstance(value, list):
                    kwargs[key] = [annotations(item) for item in value]
                elif value:
                    kwargs[key] = annotations(value)
            except Exception as e:
                logging.exception(e)
                logging.info(f'{key} 字段期待类型为: {str(annotations)} 实际为: "{value}"')
                self.finish({'code': -1, 'msg': '参数错误'})
                return

        try:  # 捕获异常，关闭连接
            if iscoroutinefunction(method) or is_coroutine_function(method):
                response = await method(self, *args, **kwargs)
            else:
                response = method(self, *args, **kwargs)
            return response
        except ParametersError as e:
            logging.exception(e)
            self.finish({'code': -1, 'msg': '参数错误'})
        except (NotFound, FileTypeError, Duplicate, PermissionDenied, InternalError) as e:
            self.finish({'code': e.code, 'msg': e.msg})
        except Finish as e:
            raise e
        except Exception as e:
            logging.exception(e)
            self.finish({'code': -1, 'msg': '内部错误'})
        finally:
            for key, model in model_dict.items():
                model.clear()

    return wrapper
