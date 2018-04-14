#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from flask import Flask
from flask_cors import *
from flask import jsonify

from AutoSummarization import utils
from AutoSummarization.utils.exceptions import HttpException
from datetime import timedelta
from AutoSummarization import config

logger = utils.getLogger(__name__)
app = Flask("AutoSummarization")
app.config["SECRET_KEY"] = config["secret_key"]
CORS(app, supports_credentials=True)
app.permanent_session_lifetime = timedelta(days=7)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"code": 400, "message": "BadRequest"})


@app.errorhandler(413)
def file_too_big(error):
    return jsonify({"code": 413, "message": "FileTooBig"})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"code": 404, "message": "NotFound"})


@app.errorhandler(405)
def method_not_support(error):
    return jsonify({"code": 405, "message": "MethodNotSupport"})


@app.errorhandler(HttpException)
def http_exception(error):
    return jsonify({"code": error.code, "message": error.message})


@app.errorhandler(Exception)
def internel_error(error):
    logger.error(error, exc_info=True)
    return jsonify({"code": 500, "message": repr(error)})
