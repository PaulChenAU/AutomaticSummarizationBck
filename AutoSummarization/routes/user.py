# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.controllers.tools import auth
from flask import request, Blueprint, jsonify

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["POST"])
def user_login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = auth.auth_password(username, password)
    return jsonify({
        "code": "1",
        "data": res
    })


@user_bp.route("/create", methods=["POST"])
def create_user():
    data = {key: value for key, value in request.json.iteritems()}
    res = auth.create_user(data)
    return jsonify({
        "code": "1",
        "data": res
    })