from .order_form import OrderFormAddHandler, OrderFormCheckHandler, OrderFormQueryHandler, OrderFormGroupHandler

urls = [
    ("/api/order_form/submit", OrderFormAddHandler),
    ("/api/order_form/check", OrderFormCheckHandler),
    ("/api/order_form/query", OrderFormQueryHandler),
    ("/api/order_form/orders_query", OrderFormGroupHandler),
]