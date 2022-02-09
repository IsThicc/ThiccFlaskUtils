
__license__ = "Apache Version 2.0"
__version__ = "1.0.0"
__authors__ = ["Mrmagicpie: <pie@mrmagicpie.xyz>"]

from types import ModuleType, FunctionType
from flask import Flask
from typing  import Iterable, Callable
from logging import getLogger

class _UtilsConfig(object):
    def __init__(self, app: Flask, **kwargs):
        self._app = app
        self.config = (kwargs if "config" not in kwargs else kwargs['config'])

    def __getitem__(self, item):
        return self.config.get(item) or self._app.config.get(item)
        # if item in self.config:
        #     return self.config[item]
        # elif item in self._app.config:
        #     return self._app.config[item]
        # return None

    def get(self, item, default=None):
        return self.__getitem__(item) or default


class ThiccUtils(object):
    _middlewares = []
    _external_middlewares = []

    def __init__(self,
                 app: Flask = None,
                 enabled_modules: Iterable = None,
                 config: dict = None):
        if app is not None:
            self.init_app(app, enabled_modules, config)

    @property
    def logger(self):
        return getLogger(__name__)

    def add_middleware(self, middleware):
        if type(middleware) is not Callable:
            raise RuntimeError(f"Cannot add '{str(middleware)}' to middleware list, object not callable.")
        self._external_middlewares.append(middleware)

    def get_middleware(self, middleware_type):
        for middleware in self._middlewares:
            if type(middleware) is middleware_type:
                return middleware

    def init_app(self, app: Flask, enabled_modules: Iterable = None, config: dict = None):
        self.config = _UtilsConfig(app=app, **config)  # noqa
        self._wsgi_app = app  # noqa

        if enabled_modules is not None:
            import flask_thiccutils  # noqa
            for mod in enabled_modules:
                module = getattr(flask_thiccutils, mod, False)
                if not module or type(module) is not ModuleType:
                    self.logger.warning(f"{mod} not found in flask_thiccutils!")
                    continue

                setup = getattr(module, "setup", False)
                if not setup:
                    self.logger.fatal(f"{mod} is not a valid module, but is found! "
                                      "Report this issue if the expected behaviour is that it works.")
                    continue

                setup_output = setup(app, self)
                setup_output_type = type(setup_output)
                if setup_output_type is not Callable:
                    continue

                if setup_output_type is FunctionType:
                    setup_output()
                    continue

                self._middlewares.append(setup_output)

    def __call__(self, environ, start_response):
        for middleware in self._middlewares:
            middleware(environ, start_response)

        for middleware in self._external_middlewares:
            try:
                middleware(environ, start_response)
            except Exception as exc:
                self.logger.fatal(f"Error in external middleware '{type(middleware)}';\n\n{str(exc)}")

        return self._wsgi_app(environ, start_response)
