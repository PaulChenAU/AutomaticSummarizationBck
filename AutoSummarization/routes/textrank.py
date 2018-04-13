# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from AutoSummarization.controllers import textrank

textrank_bp = Blueprint("textrank", __name__)


@textrank_bp.route("/history", methods=["POST"])
def textrank_summary():
    res = textrank.textrank_history()
    return jsonify({
        "code": "1",
        "data": res
    })


@textrank_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json.get("data")
    document = data.get("data").get("document")
    res = textrank.get_summary(document)
    return jsonify({
        "code": "1",
        "data": {
            "summary": res
        }
    })
