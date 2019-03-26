from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


mysql_options = {
    'pool_size': 64,
    'pool_recycle': 3599,
    'echo': 0 and options.DEBUG,
    'max_overflow': 0,
}

engines = {}


def get_engine_by_name(name, isolation_level='REPEATABLE_READ'):
    key = '{}:{}'.format(name, isolation_level)
    if key not in engines:
        engines[key] = create_engine(options.MYSQL[name], isolation_level=isolation_level, **mysql_options)
    return engines.get(key)


def get_session_by_name(name, transaction=False, **kwargs):
    """
    直接通过数据库配置名称返回对应的Session。
    transaction代表拿到的session是否支持事务
    1. transaction=True代表的意思是connection上面`set autocommit=0`。
       这个时候可以使用事务，需要手动成对调用session.begin()和session.commit()。
       主要用在有的业务一次在一个或者多个表插入多条数据的情况。
       除了保持数据一致性方面的考虑。还有就是插入性能会好很多。
    2. transaction=False代表connection上面`set autocommit=1`(这个应该是mysql默认的)。
       这个时候也能使用插入或者更新操作（会立即生效）
       这个模式下面polardb能很好的根据sql类型做负载均衡
    """
    return sessionmaker(
        bind=get_engine_by_name(
            name,
            isolation_level='REPEATABLE_READ' if transaction else 'AUTOCOMMIT',
        ),
        **kwargs,
    )


# TODO 根据自己需要在这个地方配置不同的Session
Session = get_session_by_name('master', transaction=True)



