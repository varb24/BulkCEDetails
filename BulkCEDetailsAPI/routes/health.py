from flask import Blueprint
from lcg_common.webservice import public_endpoint

mod = Blueprint("health", __name__, url_prefix="/")


@mod.route("/readyz", methods=["GET"])
@public_endpoint
def readyz():
    """
    Implies the service is ready to do its job
    """
    return "READY"


@mod.get("/livez")
@public_endpoint
def livez():
    """
    Implies the service is up and running
    """
    return "OK"
