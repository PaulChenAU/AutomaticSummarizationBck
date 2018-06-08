# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g, session
from AutoSummarization.controllers import deeplearning

deeplearning_bp = Blueprint("deeplearning", __name__)


@deeplearning_bp.route("/history", methods=["GET"])
def deeplearning_summary():
    res = deeplearning.deeplearning_history(session["user"])
    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@deeplearning_bp.route("/history", methods=["POST"])
def deeplearning_summary_page():
    data = request.json.get("data")
    page = data.get("page", 0)
    count = data.get("count")
    if count is not None:
        start = (page - 1) * count
        end = start + count
        res = deeplearning.deeplearning_history_page(session["user"], start, end)
    else:
        res = deeplearning.deeplearning_history(data)

    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@deeplearning_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json.get("data").get("data")
    res = deeplearning.get_summary(data)
    return jsonify({
        "code": "1",
        "data": {
            "summary": res
        }
    })
