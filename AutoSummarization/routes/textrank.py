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

    res = textrank.textrank_history()
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
    res = textrank.get_summary(data)
    return jsonify({
        "code": "1",
        "data": {
            "summary": res
        }
    })
