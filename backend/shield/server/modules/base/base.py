import json
import logging

from core.base_handler import BaseHandler, arguments
from settings.constant import LOG_KW
from .model import TestModel


class AnalyticsHandler(BaseHandler):
    def initialize(self, graylog=None):
        """设置将信息发送到graylog"""
        self.graylog = graylog

    @arguments
    def post(self, events=list()):
        """记录前端埋点回传信息"""
        logging.getLogger('tornado.access').info(
            f"{self.device_id} event length {len(events)}"
        )
        for event in events:
            event['device_id'] = self.device_id
            event['user_id'] = self.current_user
            event['Version'] = self.version

            for key in set(event.keys()) & LOG_KW:
                event['base_{}'.format(key)] = event.pop(key)
            try:
                self.graylog.info(
                    event.get('action') or event.get('category') or event.get('site') or '',
                    extra=event
                )
            except Exception as e:
                logging.exception(e)
                logging.info(json.dumps(event))
        self.finish()


class HealthHandler(BaseHandler):
    """负载均衡心跳检查"""
    def get(self):
        self.finish()


class TestHandler(BaseHandler):
    @arguments
    def get(self, user_id, model: TestModel = None, q: str = ''):
        logging.info("debug: %r %r %r, %r", user_id, q, model, self.session)

    def get_user(self, current_user):
        return {"current_user": current_user}

