#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import sys
import argparse
import werkzeug.serving

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from AutoSummarization import config
from AutoSummarization import utils
from AutoSummarization.app import app


reload(sys)
sys.setdefaultencoding('utf-8')


def register_blueprints(mode="normal"):
    if mode == "normal":
        from AutoSummarization.routes.summary import summary_bp
        from AutoSummarization.routes.user import user_bp
        from AutoSummarization.routes.avatar import avatar_bp
        app.register_blueprint(summary_bp, url_prefix="")
        app.register_blueprint(user_bp, url_prefix="/user")
        app.register_blueprint(avatar_bp, url_prefix="/avatar")

    elif mode == "admin":
        pass


def start_dev(mode="normal", host="127.0.0.1", port=5800):
    # werkzeug.serving.run_with_reloader()
    # register blueprints
    register_blueprints(mode)
    # set debug mode
    app.debug = True

    @werkzeug.serving.run_with_reloader
    def run_server():
        "Start gevent WSGI server"
        # use gevent WSGI server instead of the Flask
        http = WSGIServer(
            (host, port),
            app,
            handler_class=WebSocketHandler,
            log=utils.getLogger("wsgi"))
        # TODO gracefully handle shutdown
        http.serve_forever()

    run_server()


def start(mode="normal", host="127.0.0.1", port=5800):
    register_blueprints(mode)
    # set debug mode
    app.debug = False
    "Start gevent WSGI server"
    # use gevent WSGI server instead of the Flask
    http = WSGIServer(
        (host, port),
        app,
        handler_class=WebSocketHandler,
        log=utils.getLogger("wsgi")
    )
    # TODO gracefully handle shutdown
    http.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Start web server.')
    print "1"
    args = parser.parse_args()
    print args
    if args.action == "start":
        start(args.mode, args.host, args.port)
    elif args.action == "start_dev":
        start_dev(args.mode, args.host, args.port)

    else:
        print("Nothing to do.")


if __name__ == "__main__":
    start_dev()
