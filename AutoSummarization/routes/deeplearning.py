# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from AutoSummarization.controllers import deeplearning

deeplearning_bp = Blueprint("deeplearning", __name__)


@deeplearning_bp.route("/history", methods=["POST"])
def deeplearning_summary():
    res = deeplearning.deeplearning_history()
    return jsonify({
        "code": "1",
        "data": res
    })
