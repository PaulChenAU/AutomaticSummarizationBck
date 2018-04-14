# -*- coding:utf-8 -*-
# __author__=''
from AutoSummarization.controllers.tools import auth
from flask import request, Blueprint, jsonify
from flask import g, session

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["POST"])
def user_login():
    data = request.json.get("data", None)
    res = auth.auth_password(data.get("username"), data.get("password"))
    if res is not False:
        print "yes"
        session["user"] = res
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


@user_bp.route("/reset", methods=["POST"])
def reset_password():
    username = request.json.get("username", None)
    old_password, new_password = request.json.get("old_password", None), request.json.get("new_password", None)
    res = auth.reset_password(username, old_password, new_password)
    return jsonify({
        "code": "1",
        "data": res
    })


@user_bp.route("/data", methods=["POST"])
def change_user_data():
    data = request.json.get("data", None)
    res = auth.update_user(data.get("user"))
    return jsonify({
        "code": "1",
        "data": res
    })
