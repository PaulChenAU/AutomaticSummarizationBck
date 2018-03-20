# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from AutoSummarization.controllers import summary

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary", methods=["POST"])
def generate_summary():
    data = {key: value for key, value in request.json.iteritems()}
    res = summary.get_summary(data)
    return jsonify({
        "code": "1"
    })
