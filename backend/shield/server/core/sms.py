import json
import hashlib
import logging

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import options


class SMSender(object):
    def __init__(self, config=options.SENDCLOUD):
        self._sms_user = config['SENDCLOUD_SMS_USER']
        self._sms_key = config['SENDCLOUD_SMS_KEY']
        self._sms_url = config['SENDCLOUD_SMS_URL']

        self._params = {
            'smsUser': self._sms_user,
            'smsKey': self._sms_key,
        }

    def set_template_id(self, template_id):
        self._params["templateId"] = template_id

    def set_phone(self, phone):
        self._params["phone"] = str(phone)
        self._sms_send_phone = str(phone)

    def set_vars(self, vals):
        self._params["vars"] = json.dumps(vals)

    def set_signature(self):
        param_keys = list(self._params.keys())
        param_keys.sort()

        param_str = ""
        for key in param_keys:
            param_str += key + '=' + str(self._params[key]) + '&'
        param_str = param_str[:-1]

        sign_str = self._sms_key + '&' + param_str + '&' + self._sms_key
        self._params["signature"] = hashlib.md5(sign_str.encode()).hexdigest()

    async def send(self, template_id, telephone, args):
        self.set_template_id(template_id)
        self.set_phone(telephone)
        self.set_vars(args)
        try:
            HTTPRequest(url=self._sms_url, method='POST', body=json.dumps(self._params))
            res = await AsyncHTTPClient().fetch(HTTPRequest)
            json_r = json.loads(res.body.decode())
            if json_r.get('result'):
                logging.info(f"send sms to {self._sms_send_phone} success")
                return True
        except Exception as e:
            logging.exception(e)
            logging.warning(f"send sms to {self._sms_send_phone} failed")
