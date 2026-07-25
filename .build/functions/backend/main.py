import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.dirname(CURRENT_DIR)

if FUNCTIONS_DIR not in sys.path:
    sys.path.insert(0, FUNCTIONS_DIR)

import zcatalyst_sdk
from flask import Request, jsonify, make_response

from services.chat_service import chat


def handler(request: Request):
    try:
        app = zcatalyst_sdk.initialize()

        if request.path == "/chat" and request.method == "POST":
            return chat(request, app)

        return make_response(
            jsonify({"message": "Route not found"}),
            404
        )

    except Exception as e:
        return make_response(
            jsonify({"message": str(e)}),
            500
        )