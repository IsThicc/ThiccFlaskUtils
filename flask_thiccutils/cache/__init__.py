
from flask import request, Flask
from beaker.middleware import CacheMiddleware

def setup(app: Flask, utils: "flask_thiccutils.ThiccUtils"):
    @property
    def get_cache():
        return request.environ.get(utils.config.get('beaker_cache', "beaker.cache"))

    @app.before_request
    def before_request():
        setattr(request, "cache", get_cache)

    utils.logger.debug("Initialized get_cache property, and before_request handler. "
                       "Setting up CacheMiddleware (beaker.middleware.CacheMiddleware) class.")
    return CacheMiddleware(app=app,
                           environ_key=utils.config.get('beaker_cache', 'beaker.cache'),
                           **utils.config.get("beaker_settings", {})
                           )
