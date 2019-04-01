import logging

import tornado.log
import tornado.web
import tornado.ioloop
import tornado.autoreload
import tornado.httpserver
from tornado.options import options, parse_command_line

from settings.config import load_config


load_config()
parse_command_line()

tornado_settings = dict(
    debug=options.DEBUG,
    gzip=options.GZIP,
    xheaders=options.XHEADERS,
    serve_traceback=False,
    cookie_secret=options.COOKIE_SECRET
)

tornado.log.enable_pretty_logging()


class NoHealthLoggingFilter(logging.Filter):
    def __init__(self, name='NoHealthLoggingFilter'):
        logging.Filter.__init__(self, name)

    def filter(self, record):
        return not record.getMessage().startswith('200 GET /_healthz')


def main():
    from api import urls
    from core.graypy import graylog_channel

    access_log = logging.getLogger("tornado.access")
    access_log.addHandler(graylog_channel)
    access_log.addFilter(NoHealthLoggingFilter())

    application = tornado.web.Application(urls, **tornado_settings)

    server = tornado.httpserver.HTTPServer(application)
    server.listen(port=options.SERVER_PORT)
    server.start()

    logging.info("Start Success: 0.0.0.0:{}".format(options.SERVER_PORT))

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
