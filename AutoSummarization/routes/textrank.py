# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g, session
from AutoSummarization.controllers import textrank

textrank_bp = Blueprint("textrank", __name__)


@textrank_bp.route("/history", methods=["POST"])
def textrank_summary():
    data = request.json.get("data")
    page = data.get("page", 0)
    count = data.get("count")
    if count is not None:
        start = (page - 1) * count
        end = start + count
        res = textrank.textrank_history_page(session["user"], start, end)
    else:
        res = textrank.textrank_history(data)

    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@textrank_bp.route("/history", methods=["GET"])
def get_textrank_summary():
    res = textrank.textrank_history(session["user"])
    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@textrank_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json.get("data").get("data")
    compress_rate = request.json.get("data").get("compressrate", "50%")
    compress_rate_val = float(compress_rate[:len(compress_rate)-1]) / 100
    res = textrank.get_summary(data, compress_rate_val)
    return jsonify({
        "code": "1",
        "data": {
            "summary": res
        }
    })
