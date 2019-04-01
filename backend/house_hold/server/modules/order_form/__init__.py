from .order_form import OrderFormAddHandler, OrderFormCheckHandler, OrderFormQueryHandler

urls = [
    ("/api/order_form/submit", OrderFormAddHandler),
    ("/api/order_form/check", OrderFormCheckHandler),
    ("/api/order_form/query", OrderFormQueryHandler),
]