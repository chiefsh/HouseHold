import base64
import json
import logging
from tornado.options import options
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from Crypto.Cipher import AES


class WeiXinApp:
    def __init__(self, config=options.WX_APP):
        self.app_id = config['app_id']
        self.app_secret = config['app_secret']

    async def jscode2session(self, js_code):
        """由微信小程序临时登录凭证获取 session_key 和 open_id"""
        url = '{api}?appid={appid}&secret={secret}&js_code={code}&grant_type={grant_type}'.format(
            api='https://api.weixin.qq.com/sns/jscode2session',
            appid=self.app_id,
            secret=self.app_secret,
            code=js_code,
            grant_type='authorization_code',
        )
        try:
            request = HTTPRequest(url=url, method='GET')
            response = await AsyncHTTPClient().fetch(request)
            res = json.loads(response.body.decode())
        except Exception as e:
            logging.exception(e)
            return False
        logging.info(res)
        if 'session_key' in res and 'open_id' in res:
            return res
        return False

    def decode_encrypted_data(self, encrypted_data, iv, session_key):
        """解密用户数据"""
        session_key = base64.b64decode(session_key)
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)

        cipher = AES.new(session_key, AES.MODE_CBC, iv)

        try:
            decode = self._unpad(cipher.decrypt(encrypted_data))
            decrypted = json.loads(decode.decode())
        except Exception as e:
            logging.exception(e)
            raise Exception('Invalid Buffer', encrypted_data)

        if decrypted['watermark']['appid'] != self.app_id:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]
