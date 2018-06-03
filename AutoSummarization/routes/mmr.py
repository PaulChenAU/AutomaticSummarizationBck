# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g, session
from AutoSummarization.controllers import mmr

mmr_bp = Blueprint("mmr", __name__)


@mmr_bp.route("/history", methods=["POST"])
def mmr_summary():
    data = request.json.get("data")
    page = data.get("page", 0)
    count = data.get("count")
    if count is not None:
        start = (page - 1) * count
        end = start + count
        res = mmr.mmr_history_page(session["user"], start, end)
    else:
        res = mmr.mmr_history(data)

    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@mmr_bp.route("/history", methods=["GET"])
def get_mmr_summary():
    res = mmr.mmr_history(session["user"])
    return jsonify({
        "code": "1",
        "data": {
            "history": res
        }
    })


@mmr_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json.get("data").get("data")
    compress_rate = request.json.get("data").get("compressrate", "50%")
    res = mmr.get_summary(data, compress_rate)
    return jsonify({
        "code": "1",
        "data": {
            "summary": res
        }
    })
