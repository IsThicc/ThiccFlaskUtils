#
#                         ThiccFlaskUtils __init__.py | 2020-2022 (c) IsThicc
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
from flask import Flask
from beaker.middleware import CacheMiddleware
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
def setup(app: Flask, utils: "flask_thiccutils.ThiccUtils"):

    # @app.before_request
    # def before_request():
    #     # utils.logger.fatal("aaaaaaaaaa")
    #     setattr(request, "cache", get_cache)

    class CacheRequest(app.request_class):
        @property
        def cache(self):
            return self.environ.get(utils.config.get('beaker_cache', "beaker.cache"))

    app.request_class = CacheRequest
    utils.logger.debug("Initialized get_cache property. "  # and before_request handler. "
                       "Setting up CacheMiddleware (beaker.middleware.CacheMiddleware) class.")

    return CacheMiddleware(app=utils.middleware_wsgi,
                           environ_key=utils.config.get('beaker_cache', 'beaker.cache'),
                           **utils.config.get("beaker_settings", {})
                           )

#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
