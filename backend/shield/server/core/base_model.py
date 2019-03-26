from collections import namedtuple

from sqlalchemy import func, sql
from sqlalchemy.orm.scoping import scoped_session

from core.mysql import get_session_by_name
from core.redisdb import redis_cli

Context = namedtuple("HandlerContext", "current_user")  # example


class ContextMaker:
    """example：model需要的上下文，与RequertHandler解耦"""

    def __call__(self, *args, **kwargs):
        return Context(current_user=None)


class HandlerContextMaker(ContextMaker):
    """接收一个RequertHandler实例，生成用于model的上下文"""

    def __call__(self, handler):
        return Context(current_user=handler.current_user)


# default handler context for model
HandlerContext = HandlerContextMaker()


class BaseModel(object):
    """model基类，约定上下文"""

    def __init__(self, *args, context: Context = None, **kwargs):
        self.context = context
        if context and context.current_user:
            setattr(self, 'current_user', context.current_user)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def clear(self):
        """释放资源"""


class MysqlModel(BaseModel):
    """用于连接mysql的model"""

    def __init__(self, *args, engine='master', **kwargs):
        self.engine = engine
        super().__init__(*args, **kwargs)

    def _create_session(self, transaction=True):
        return scoped_session(
            get_session_by_name(
                self.engine,
                transaction=transaction,
                expire_on_commit=False,
                autocommit=True,
            ),
            scopefunc=lambda: self
        )

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = self._create_session()
        return self._session

    @property
    def slave_session(self):
        """虽然叫做slave_session，但是和前面的session区别仅仅在于不使用事务，照样可以更新数据"""
        if not hasattr(self, '_slave_session'):
            self._slave_session = self._create_session(transaction=False)
        return self._slave_session

    def query_one_page(self, query, page, size):
        """查询一页"""
        if size <= 0:
            return []
        offset = (page - 1) * size
        # TODO 这里也可以强行使用self.slave_session
        return query.offset(offset if offset > 0 else 0).limit(size if size < 100 else 100).all()

    def query_total(self, query):
        """查询总数"""
        if query._limit:
            return query.with_entities(
                sql.literal_column('1')
            ).count() or 0
        if query._group_by:
            return query.with_entities(
                sql.literal_column('1')
            ).order_by(None).count() or 0
        return self.slave_session.execute(
            query.with_labels().statement.with_only_columns(
                [func.count(1)]
            ).order_by(None)
        ).scalar() or 0

    def clear(self):
        """释放连接"""
        if hasattr(self, '_session'):
            self._session.remove()
        if hasattr(self, '_slave_session'):
            self._slave_session.remove()
        super().clear()


class RedisModel(BaseModel):
    """用于连接 redis 的 model"""

    def __init__(self, *args, **kwargs):
        self.redis_client = redis_cli()
        super().__init__(*args, **kwargs)

