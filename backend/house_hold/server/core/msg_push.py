import json
import logging
from functools import reduce
from bson import ObjectId
from urllib import parse as urlparse

from tornado.options import options
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class PushService(object):
    """消息推送服务"""
    def __init__(self, api=options.PUSH_API, app=options.PUSH_APP):
        self.app = app
        self.api = api

    def _rshift(self, val, n):
        return (val % 0x100000000) >> n

    def _hashcode(self, s):
        return '{:x}'.format(self._rshift(reduce(lambda p, c: (p << 5) - p + ord(c), s, 0), 0))

    def _channel(self, app, uid):
        app = ('0' * 16 + str(app))[-16:]
        if not ObjectId.is_valid(uid):
            uid = ('0' * 16 + str(uid))[-16:]
            chanel = '-'.join([self._hashcode(app), self._hashcode(uid)])
        else:
            chanel = '-'.join([self._hashcode(app), uid])
        return '-'.join([chanel, self._hashcode(chanel[::-1])])

    async def push(self, user_id, message):
        """将指定消息推送给指定用户"""
        url = '{}?id={}'.format(self.api, self._channel(self.app, str(user_id)))
        logging.info("push msg on: {}".format(url))
        message['app'] = self.app
        message['user_id'] = user_id
        request = HTTPRequest(
            url=url,
            method='POST',
            body=urlparse.quote(json.dumps(message, separators=(',', ':'))),
            request_timeout=5
        )
        response = await AsyncHTTPClient().fetch(request)
        logging.info("push message to user {}: {}".format(user_id, message))
        return json.loads(response.body.decode('utf-8') or '{}')


if __name__ == '__main__':
    from tornado.options import define
    from tornado.ioloop import IOLoop

    define('PUSH_API', default="http://192.168.11.186:1302/pub")
    define('PUSH_APP', default="webtalentdev")

    async def main():
        push = PushService(options.PUSH_API, options.PUSH_APP)
        res = await push.push(3291, {
            "action": "list_scan_finished",
            "message": {
                'list_id': 4563,
                'name': "teste",
                'item_count': 100,
                'scan_count': 100,
                'match_count': 73,
                'not_scan_count': 0,
                'is_read': 0,
            }
        })
        print(res)

    IOLoop.current().run_sync(main)
