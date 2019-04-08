from .product import ProductAddHandler, ProductDeleteHandler, ProductQueryHandler, ProductIsTopHandler, ProductSortedHandler

urls = [
    ("/api/product/add", ProductAddHandler),
    ("/api/product/delete", ProductDeleteHandler),
    ("/api/product/query", ProductQueryHandler),
    ("/api/product/is_top", ProductIsTopHandler),
    ("/api/product/up", ProductSortedHandler),
]