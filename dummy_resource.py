from flask import Flask
from base import BindAPI, ResourceAPI
from utils import authorization_required, register_api, add_property, add_action


@register_api(
    identification="webeng:resource:dummy:test",
    title="WebEng-Resource-Dummy-test",
    description="Dummy resource api"
)
class DummyResourceAPI(ResourceAPI):
    @authorization_required
    @add_property(
        name="resource",
        title="Show resource status",
        description="Example of property method",
        properties={"status": "string"},
        url="/resource",
        security="basic_sc"
    )
    def get(self):
        pass

    @authorization_required
    def post(self, action):
        if action == "example":
            self.example()

    @add_action(
        name="example",
        title="Example method of action",
        description="Example method of action",
        output={"status": "string"},
        url="/resource/example",
        security="basic_sc"
    )
    def example(self):
        pass

    @staticmethod
    def add_url_rule(_app):
        # TODO may can be automated by using decorators
        view = DummyResourceAPI.as_view('resource_api')
        # Dummy resource API View
        _app.add_url_rule('/resource', view_func=view, methods=['GET', ])
        _app.add_url_rule('/resource/<action>', view_func=view, methods=['POST', ])


# Run server
app = Flask(__name__)
BindAPI.add_url_rule(app)
DummyResourceAPI.add_url_rule(app)

# app.run(host='0.0.0.0', port=8001)
