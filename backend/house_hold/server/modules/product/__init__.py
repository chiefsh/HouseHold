from .product import ProductAddHandler, ProductDeleteHandler, ProductQueryHandler

urls = [
    ("/api/product/add", ProductAddHandler),
    ("/api/product/delete", ProductDeleteHandler),
    ("/api/product/query", ProductQueryHandler),
]