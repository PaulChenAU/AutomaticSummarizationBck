# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from AutoSummarization.controllers import deeplearning

deeplearning_bp = Blueprint("deeplearning", __name__)


@deeplearning_bp.route("/history", methods=["POST"])
def deeplearning_summary():
    res = deeplearning.deeplearning_history()
    return jsonify({
        "code": "1",
        "data": res
    })


@deeplearning_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json.get("data")
    res = deeplearning.get_summary(data)
    return jsonify({
        "code": "1"
    })
