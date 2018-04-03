from flask import Flask

from app import routes


def create_app():
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    # app.config.from_object(config_object)
    # register_extensions(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(routes.api.api_bp)
    app.register_blueprint(routes.index.webpage_bp)
    return None

