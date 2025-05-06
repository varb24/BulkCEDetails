"""
File for the general endpoint creation.
Once names in <> are filled in:
1) import the new endpoint file into server.py file
2) Add a Blueprint object at the end of server.py with your endpoint's filename
    a) app.register_blueprint(<endpoint_name>.mod)
"""
import logging

from flask import Blueprint, jsonify, session
from lcg_common.webservice import (
    auth_required,
)

from <api_name>.helpers import <helper_func>

mod = Blueprint("root", __name__, url_prefix="/")


@mod.route("<route_url>")
@auth_required
def <index>():
    """

    """
    response = {}
    return response