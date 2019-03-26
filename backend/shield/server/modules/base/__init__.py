from tornado.web import StaticFileHandler

from core.graypy import graylog
from .base import HealthHandler, AnalyticsHandler, TestHandler

urls = [
    # for test
    ("/api/test/([0-9a-f]{24})", TestHandler),
    ("/_healthz", HealthHandler),
    ("/api/analytics", AnalyticsHandler, dict(graylog=graylog)),
    ("/(.*)", StaticFileHandler, {'path': '/server/dist'})
]
