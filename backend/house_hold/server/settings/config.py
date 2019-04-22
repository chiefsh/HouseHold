import os
from tornado.options import define, parse_config_file


def load_config():
    # 服务器配置
    define("DEBUG", default=True)
    define("SERVER_PORT", default=8888)

    define("GZIP", default=True)
    define("XHEADERS", default=True)
    # TODO
    define("COOKIE_SECRET", default="__SHIELD__: SHIELD_2018_07_16")
    define("MODULES", default=['account', 'image', 'product', 'basic', 'category', 'community',
                               'order_form', 'region', 'base'])

    define("AUTH_TOKEN_SALT", default="")
    define("SIGNED_SECRET", default="SIGNED_SECRET")

    # MySQL 配置
    define("MYSQL", default={
        "master": "mysql+pymysql://root:House_hold2019@127.0.0.1:3306/house_hold?charset=utf8",
    })

    # ElasticSearch 配置
    define("ES_SERVER", default=["elasticsearch"])

    # RabbitMQ 配置
    define("RABBIT_MQ_SERVER", default="127.0.0.1")
    define("RABBIT_MQ_PORT", default=5672)

    # Redis 配置
    define("REDIS_HOST", default="127.0.0.1")
    define("REDIS_PORT", default=6379)
    define("REDIS_DB", default=1)
    define("REDIS_NAMESPACE", default="shield")

    # GRAYLOG 日志
    define("GELF_HOST", default='192.168.11.186')
    define("GELF_PORT", default=12202)

    # 外部关联系统
    # 消息推送服务
    """
    'test': 'weseektest',
    """
    define('PUSH_APP', default="weseektest")
    define('PUSH_API', default="http://192.168.11.186:1302/pub")

    # loading config from *.conf
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_file = os.path.join(root_path, "etc", "web_config.conf")
    if os.path.isfile(config_file):
        parse_config_file(config_file)
