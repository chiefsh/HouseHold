import pika
from pika.exceptions import ChannelClosed, ConnectionClosed
import logging

from tornado.options import options


class Singleton(type):
    """
    由于系统中很多地方直接使用的下面的代码发送消息
    pikachu = MqSession()
    pikachu.put(queue, json.dumps({ ... }))
    pikachu.close()
    所以每次创建连接和关闭连接，在消息比较多的时候造成挺大的内存和性能上面的开销
    考虑使用单例模式，只会有一个连接，在put消息的时候会自动重连，并且重试一次推送消息
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MqSession(object, metaclass=Singleton):

    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.credentials = pika.PlainCredentials(username='spider', password='spider')
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=options.RABBIT_MQ_SERVER,
                credentials=self.credentials,
                blocked_connection_timeout=2,  # 设置2秒超时，避免阻塞
                port=options.RABBIT_MQ_PORT,
            ))
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)
        except Exception as e:
            logging.exception(e)
            return

    def _put(self, queue, body, priority=0, expiration=None):
        self.channel.basic_publish(
            exchange='spider',
            routing_key=queue,
            body=body.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 2=消息持久话
                priority=priority,
                expiration=expiration and str(expiration) or None,
            ),
        )

    def put(self, queue, body, priority=0, expiration=None):
        try:
            self._put(queue, body, priority, expiration)
        except (ConnectionClosed, ChannelClosed) as e:
            logging.warning("reconnect and push msg: {} to queue: {}".format(body, queue))
            try:
                self.connection.close()
            except Exception as e:
                logging.warn("exception for close connection %r", e)
            self.connect()
            self._put(queue, body, priority, expiration)
        except Exception as e:
            logging.exception(e)
            logging.warning("push msg: {} to queue: {} failed".format(body, queue))
            return -1

    def get(self, queue):
        try:
            for method_frame, properties, body in self.channel.consume(queue):
                return method_frame.delivery_tag, body.decode('utf-8')
        except Exception as e:
            logging.exception(e)
            return None

    def ack(self, delivery_tag):
        try:
            self.channel.basic_ack(delivery_tag)
        except Exception as e:
            logging.exception(e)
            return -1

    def close(self):
        # 使用单例模式之后，不用每次都创建连接，所以就不用真实的关闭连接了
        # 在程序退出的时候自动的关闭连接
        # self.connection.close()
        pass

