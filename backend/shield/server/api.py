from tornado.options import options


# https://docs.python.org/3/library/functions.html#__import__
def load_module(name):
    module = __import__('modules.{}'.format(name))
    return getattr(module, name).urls


def load_modules(modules):
    app_api = []
    for module in modules:
        app_api = app_api + load_module(module)
    return app_api


urls = load_modules(options.MODULES)
