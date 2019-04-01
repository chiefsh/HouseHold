from .category import CategoryAddHandler, CategoryQueryHandler, CategoryDeleteHandler

urls = [
    ("/api/category/add", CategoryAddHandler),
    ("/api/category/query", CategoryQueryHandler),
    ("/api/category/delete", CategoryDeleteHandler),
]