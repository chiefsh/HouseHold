import pika
import logging
from pika import adapters
from tornado import ioloop


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


CUSTOMER_IOLOOP = ioloop.IOLoop.instance()
DEFAULT_CONNECT_PARAS = {  # see pika.URLParameters
    "socket_timeout": 15,
    "heartbeat": 5,
}


class BaseConsumer(object):
    """消费者基类，处理 connect 和 channel 异常并重试"""
    EXCHANGE = 'spider'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'extract-result-queue'
    ROUTING_KEY = 'extract-result-queue'
    ARGUMENTS = {}  # 这个用来处理队列需要配置x-message-ttl和x-dead-letter-exchange的情况

    def __init__(
        self, amqp_url,
        exchange='spider',
        exchange_type='direct',
        queue='test',
        routing_key=None,
        prefetch_count=10,
        connect_paras=DEFAULT_CONNECT_PARAS,
        arguments=None,
    ):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = self._extend_url(amqp_url, connect_paras)

        self.EXCHANGE = exchange
        self.EXCHANGE_TYPE = exchange_type
        self.QUEUE = queue
        self.ROUTING_KEY = routing_key
        self.PREFETCH_COUNT = prefetch_count
        self.ARGUMENTS = arguments

    def _extend_url(self, url, connect_paras):
        """拓展连接参数"""
        if not (connect_paras and isinstance(connect_paras, dict)):
            logging.warning("connect_paras should be a key-value dictionary")
            return url

        query_paras = []
        for key, value in connect_paras.items():
            query_paras.append("{}={}".format(key, value))

        query_str = "&".join(query_paras)
        return url + "?" + query_str

    def run(self):
        """步骤0：启动消费者"""
        self.connect()
        CUSTOMER_IOLOOP.start()

    def connect(self):
        """步骤1：连接到队列"""
        LOGGER.info('Connecting to %s', self._url)
        self._connection = adapters.TornadoConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_open_error_callback,
            on_close_callback=self.on_connection_closed,
            custom_ioloop=CUSTOMER_IOLOOP,
        )

    def on_open_error_callback(self, connection, exception):
        """步骤1-1：连接到队列失败，5秒后重连"""
        self.reconnect(delay=5)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """步骤1-2：连接被关闭，立即重连"""
        self.reconnect(delay=0)

    def reconnect(self, delay=5):
        """重试步骤1：连接到队列"""
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
            CUSTOMER_IOLOOP.stop()
        else:
            LOGGER.warning('Connection closed, reopening in {} seconds'.format(delay))
            self._connection.close()
            CUSTOMER_IOLOOP.add_timeout(delay, self.connect)

    def on_connection_open(self, unused_connection):
        """步骤2：连接到队列后，打开channel"""
        LOGGER.info('Connection opened')
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """步骤3：打开channel后，设置 exchange"""
        LOGGER.info('Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        LOGGER.info('Declaring exchange %s', self.EXCHANGE)
        self._channel.exchange_declare(
            self.on_exchange_declareok,
            self.EXCHANGE,
            self.EXCHANGE_TYPE,
            durable=True
        )

    def on_channel_closed(self, channel, reply_code, reply_text):
        """步骤3-1：channel被关闭后，关闭连接"""
        LOGGER.warning('Channel %i was closed: (%s) %s', channel, reply_code, reply_text)
        self._connection.close()

    def on_exchange_declareok(self, unused_frame):
        """步骤4：设置 exchange 后，设置 queue"""
        LOGGER.info('Exchange declared')
        LOGGER.info('Declaring queue %s', self.QUEUE)
        self._channel.queue_declare(self.on_queue_declareok, self.QUEUE, durable=True, arguments=self.ARGUMENTS)

    def on_queue_declareok(self, method_frame):
        """步骤5：绑定 exchange 和 queue"""
        LOGGER.info('Binding %s to %s with %s', self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE, self.EXCHANGE, self.ROUTING_KEY)

    def on_bindok(self, unused_frame):
        """步骤6：绑定成功后，监听并获取队列消息"""
        LOGGER.info('Queue bound')
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

        LOGGER.info('Issuing consumer related RPC commands')
        self._channel.basic_qos(prefetch_count=self.PREFETCH_COUNT)
        self._consumer_tag = self._channel.basic_consume(self.on_message, self.QUEUE)

    def on_consumer_cancelled(self, method_frame):
        """步骤6-1：被 server 取消后，关闭 channel"""
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r', method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """步骤7：接收到消息后，开启协程处理消息"""
        LOGGER.info('Received message # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body)
        CUSTOMER_IOLOOP.spawn_callback(self.process_message_on_exception, basic_deliver.delivery_tag, properties.app_id, body)

    async def process_message_on_exception(self, tag, app_id, body):
        """步骤8：处理并确认消息，捕获未处理的异常并将未处理的消息放回队列"""
        try:
            await self.process_message(tag, app_id, body)
        except Exception as e:
            LOGGER.exception(e)
            self.reject_message(tag)

    async def process_message(self, tag, app_id, body):
        """步骤8-1：子类继承实现改该方法，处理并确认消息"""
        LOGGER.info("tag: %r app_id: %r body: %r", tag, app_id, body)
        self.acknowledge_message(tag)

    def acknowledge_message(self, delivery_tag):
        """步骤8-2：确认消息"""
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def reject_message(self, delivery_tag, requeue=True):
        """步骤8-3：拒绝消息，放回队列"""
        LOGGER.info('Reject message %s', delivery_tag)
        self._channel.basic_reject(delivery_tag, requeue=requeue)

    def stop_consuming(self):
        """步骤9：停止监听消息"""
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """步骤10：关闭 channel"""
        LOGGER.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """关闭 channel"""
        LOGGER.info('Closing the channel')
        self._channel.close()

    def close_connection(self):
        """关闭连接"""
        LOGGER.info('Closing connection')
        self._connection.close()

    def stop(self):
        """ CTRL-C stop consumer"""
        LOGGER.info('Stopping')
        self._closing = True
        self.stop_consuming()
        CUSTOMER_IOLOOP.stop()
        LOGGER.info('Stopped')


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    consumer = BaseConsumer('amqp://spider:spider@127.0.0.1:5672/%2F', queue='test')
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()


if __name__ == '__main__':
    main()
