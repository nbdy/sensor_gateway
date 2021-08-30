from flask import Flask, jsonify, request

from procpy import Process


class API(Process):
    def __init__(self, database_uri: str):
        Process.__init__(self)
        app = Flask("SensorServer")
        self.register_routes(app)
        self.app = app

    @classmethod
    def register_routes(cls, app):
        @app.route("/door")
        def door():
            print(request.args)
            return jsonify({})

        @app.route("/camera", methods=["POST"])
        def camera():
            print(request.args)
            return jsonify({})

    def run(self) -> None:
        self.app.run("0.0.0.0", 42000, debug=True)
