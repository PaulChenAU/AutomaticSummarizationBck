# -*- coding:utf-8 -*-
# __author__=''
from __future__ import unicode_literals

import flask
from flask import Blueprint
from flask import send_file
from flask import jsonify
from flask import request
from flask import app
from AutoSummarization.controllers import avatar

avatar_bp = Blueprint("avatar", __name__)


@avatar_bp.route("/<username>/<avatar_size>", methods=["GET"])
def generate_avatar(username, avatar_size):
    res = avatar.get_avatar(username, avatar_size)
    return send_file(res["file_path"]
                     , mimetype=res["mimetype"])
