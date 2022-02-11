#
#                         ThiccFlaskUtils __init__.py | 2020-2022 (c) IsThicc
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
__license__ = "Apache Version 2.0"
__version__ = "1.0.0"
__authors__ = ["Mrmagicpie: <pie@mrmagicpie.xyz>"]
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
from types import FunctionType
from flask import Flask
from typing  import Iterable, Callable
from logging import getLogger, INFO
from importlib import import_module
from flask.logging  import default_handler
from werkzeug.utils import cached_property
from werkzeug.routing import Map, Rule
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
class _UtilsConfig(object):
    def __init__(self, app: Flask, **kwargs):
        self._app = app
        self.config = (kwargs if "config" not in kwargs else kwargs['config'])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __getitem__(self, item):
        return self.config.get(item) or self._app.config.get(item)
        # if item in self.config:
        #     return self.config[item]
        # elif item in self._app.config:
        #     return self._app.config[item]
        # return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get(self, item, default=None):
        return self.__getitem__(item) or default

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ThiccUtils(object):
    _middlewares = []
    _external_middlewares = []

    _app = None
    _wsgi_app = None
    _ignored_paths = set()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self,
                 app: Flask = None,
                 enabled_modules: Iterable = None,
                 config: dict = None,
                 logLevel = INFO):
        self.logger.setLevel(logLevel)
        self.logger.debug(f"Set the log level to {str(logLevel)}")

        if app is not None:
            self.init_app(app, enabled_modules, config)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def ignoredRoute(self, f):
        """
        A decorator for ignoring a route from this and the accompanying middlewares.

            >>> @<FlaskUtils instance>.ignoredRoute
            >>> @app.route("/")
            >>> def index_route():
            >>> return "this route is ignored"

        :param f: The route function. This decorator should be places above the `@app.route` decorator, or
            called **after** the route has been registered if being registered manually.
        :return: This decorator has no direct return.
        """
        self._ignored_paths.add(
            # Determining the path of the function given from it's name
            self._app.url_map._rules_by_endpoint[f.__name__][0].rule  # noqa
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def wsgi_app(self):
        return self._wsgi_app

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @cached_property
    def logger(self):
        logger = getLogger('flask_thiccutils')
        logger.addHandler(default_handler)
        return logger

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_middleware(self, middleware):
        if type(middleware) is not Callable:
            raise RuntimeError(f"Cannot add '{str(middleware)}' to middleware list, object not callable.")
        self._external_middlewares.append(middleware)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_middleware(self, middleware_type):
        for middleware in self._middlewares:
            if type(middleware) is middleware_type:
                return middleware

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def init_app(self,
                 app: Flask,
                 enabled_modules: Iterable = None,
                 config: dict = None,
                 wsgi_app: Callable = None) -> "ThiccUtils":
        """
        Initialize the Flask middleware with all necessary attributes.
        :param app: Your `flask.Flask` object, not the `Flask.wsgi_app` object!
        :param enabled_modules: Your ThiccUtils modules to initialize for your app.
        :param config: Any additional config options that you may want for the modules.
        :param wsgi_app: An optional option for if you want to specify a different WSGI app
            to call instead of the default `flask.Flask.wsgi_app`
        :return: Returns the instance of this class.
        """
        self._app = app  # noqa
        self.config = _UtilsConfig(app=app, **(config or {}))  # noqa
        self._wsgi_app = (  # noqa
                wsgi_app or (app.wsgi_app if type(app.wsgi_app) is not type(self) else app.wsgi_app.wsgi_app)
        )

        if enabled_modules is not None:
            import flask_thiccutils  # noqa
            for mod in enabled_modules:
                # module = getattr(flask_thiccutils, mod, False)
                try:
                    module = import_module(f"flask_thiccutils.{mod}")
                except ImportError:
                    # module = False
                    # if not module:  # or type(module) is not ModuleType:
                    self.logger.warning(f"{mod} not found in flask_thiccutils!")
                    continue

                setup = getattr(module, "setup", False)
                if not setup:
                    self.logger.fatal(f"{mod} is not a valid module, but is found! "
                                      "Report this issue if the expected behaviour is that it works.")
                    continue

                setup_output = setup(app, self)
                if not callable(setup_output):
                    continue

                if type(setup_output) is FunctionType:
                    setup_output()
                    continue

                self.logger.info(f"{mod} module initialized.")
                self._middlewares.append(setup_output)
                self.logger.debug(f"Added {mod} to internal middlewares")
        return self

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def middleware_wsgi(environ, start_response):
        pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __call__(self, environ, start_response):
        if self._ignored_paths:
            try:
                Map([Rule(path) for path in self._ignored_paths])\
                    .bind_to_environ(environ).match()

                self.logger.debug(f"Path '{environ['REQUEST_URI']}' is ignored.")
                return self._wsgi_app(environ, start_response)
            except Exception as e:
                # The current path didn't match, therefore it's not supposed to be ignored
                pass

        for middleware in self._middlewares:
            middleware(environ, start_response)

        for middleware in self._external_middlewares:
            try:
                middleware(environ, start_response)
            except Exception as exc:
                self.logger.fatal(f"Error in external middleware '{type(middleware)}';\n\n{str(exc)}")

        return self._wsgi_app(environ, start_response)

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
