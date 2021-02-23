#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from gevent import monkey

monkey.patch_all()

from mephisto.abstractions.architects.router.flask.mephisto_flask_blueprint import (
    MephistoRouter,
    mephisto_router,
)
from geventwebsocket import WebSocketServer, Resource
from werkzeug.debug import DebuggedApplication


from flask import Flask

flask_app = Flask(__name__)
flask_app.register_blueprint(mephisto_router, url_prefix=r"/")

if __name__ == "__main__":
    WebSocketServer(
        ("", 3000),
        Resource([("^/.*", MephistoRouter), ("^/.*", DebuggedApplication(flask_app))]),
        debug=False,
    ).serve_forever()