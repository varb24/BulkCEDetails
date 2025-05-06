from flask import Blueprint
from lcg_common.webservice import (
    auth_required,
)

from recommendationAPI.helpers.utils import welcome_message

mod = Blueprint("root", __name__, url_prefix="/")


@mod.route("/")
@auth_required
def index():
    """
    Welcome to the root of the server, there's not much here now, and there will likely never be anything.
    """
    return welcome_message()
