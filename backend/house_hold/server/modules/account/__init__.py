from .account import LoginHandler, LoginOutHandler, AccountAddHandler, AccountQueryHandler



urls = [
    ("/api/login", LoginHandler),
    ("/api/loginout", LoginOutHandler),
    ("/api/account/add", AccountAddHandler),
    ("/api/account/query", AccountQueryHandler),
]