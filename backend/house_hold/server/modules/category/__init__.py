from .category import CategoryAddHandler, CategoryQueryHandler, CategoryDeleteHandler, CategoryIsTopHandler, CategorySortHandler

urls = [
    ("/api/category/add", CategoryAddHandler),
    ("/api/category/query", CategoryQueryHandler),
    ("/api/category/delete", CategoryDeleteHandler),
    ("/api/category/top", CategoryIsTopHandler),
    ("/api/category/up", CategorySortHandler),
]