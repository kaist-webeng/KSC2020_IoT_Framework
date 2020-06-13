from flask import Flask
from base import BindAPI, ResourceAPI, authentication_required


class DummyAPI(ResourceAPI):
    @authentication_required
    def post(self, action):
        pass

    @staticmethod
    def add_url_rule(_app):
        view = DummyAPI.as_view('resource_api')
        # Dummy resource API View
        _app.add_url_rule('/resource', view_func=view, methods=['GET', ])
        _app.add_url_rule('/resource/<action>', view_func=view, methods=['POST', ])


# Run server
if __name__ == "__main__":
    app = Flask(__name__)
    BindAPI.add_url_rule(app)
    DummyAPI.add_url_rule(app)

    app.run(host='0.0.0.0', port=5000)
