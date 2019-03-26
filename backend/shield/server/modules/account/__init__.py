from .account import LoginHandler, LoginOutHandler



urls = [
    ("/api/login", LoginHandler),
    ("/api/loginout", LoginOutHandler)
]