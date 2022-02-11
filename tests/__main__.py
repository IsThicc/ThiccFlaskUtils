
import logging, os
from flask import Flask, request
from flask_thiccutils import ThiccUtils

app = Flask(__name__)
utils = ThiccUtils(logLevel=logging.DEBUG)
app.wsgi_app = utils.init_app(app=app,
                              enabled_modules={"cache", "blueprints"},
                              config={'blueprint_dir': os.path.abspath("tests/blueprints")})

app.logger.setLevel(logging.DEBUG)

@utils.ignoredRoute
@app.route("/test")
def test():
    return "test"

@app.route("/")
def index():

    c = request.cache.get_cache("urmom", expire=1000)
    try:
        return c.get("e")
    except:
        pass

    c.put("e", "e")
    return "working"

app.run()
