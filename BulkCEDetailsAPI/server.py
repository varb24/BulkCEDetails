import logging

from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from lcg_common import config_var, get_mongodb_client, load_env, setup_logging
from lcg_common.webservice import AuthManager, HALOFlask

# Import blueprints
from BulkCEDetailsAPI.routes import (  # noqa: E402
    root,
    health
)

load_env(".env")

setup_logging(log_level="DEBUG")


app = HALOFlask(__name__)
auth_manager = AuthManager(app)


cors_kwargs = {"supports_credentials": True}

# Allow CORS debugging
if config_var("DEBUG_CORS", default=False):
    logging.warning("CORS debugging is enabled")
    logging.getLogger("flask_cors").level = logging.DEBUG

# Default config of CORS
CORS(app, **cors_kwargs)


app.config["SECRET_KEY"] = config_var("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = config_var("SESSION_TYPE", default="sqlalchemy")

if config_var("SESSION_TYPE") == "sqlalchemy":
    app.config["SQLALCHEMY_DATABASE_URI"] = config_var("SQLALCHEMY_DATABASE_URI")
    db = SQLAlchemy(app)
    app.config["SESSION_SQLALCHEMY"] = db
elif config_var("SESSION_TYPE") == "mongodb":
    app.config["SESSION_MONGODB"] = get_mongodb_client()
    app.config["SESSION_MONGODB_DB"] = config_var("SESSION_MONGODB_DB", default="recommend")
    app.config["SESSION_MONGODB_COLLECT"] = config_var("SESSION_MONGODB_COLLECT", default="sessions")


Session(app)


# Register blueprints
app.register_blueprint(root.mod)
app.register_blueprint(health.mod)


auth_manager.security_preflight()
