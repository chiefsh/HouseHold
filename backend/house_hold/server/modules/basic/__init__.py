from .basic import BasicQueryHandler, BasicUpdateHandler

urls = [
    ("/api/basic/update", BasicUpdateHandler),
    ("/api/basic/query", BasicQueryHandler),
]