"""
    Basic resource-controller and service classes for WebEng IoT testbed project

    by KyeongDeok Baek kyeongdeok.baek@kaist.ac.kr
    based on the works of:
        MinHyeop Kim soulflight@kaist.ac.kr
        MoonYoung Lee vk8520@kaist.ac.kr
        SangHoon Kim seiker@kaist.ac.kr
        Dae-Young Park mainthread@kaist.ac.kr
        JungYeon Sohn jungyeon.sohn@kaist.ac.kr

    refer https://flask.palletsprojects.com/en/1.1.x/views/
"""
import redis

from abc import abstractmethod
from flask import abort, request, jsonify, make_response
from flask.views import MethodView

from utils import abort_json, authentication_required, authorization_required, add_property, add_action


class API(MethodView):
    """
    API: basic API
    """
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class BindAPI(API):
    """
    BindAPI: API for bind/unbind user to the resource.
    After a user is bound to the resource, the user becomes the owner of the resource until unbound himself/herself
    """

    def get(self):
        """
        get: responses currently bound user's ID
        :return: [flask HTTP response in JSON] bound user's ID
        """
        response = make_response(jsonify({
            "bound": self.redis.exists('user_id'),
            "userId": self.redis.get('user_id')
        }), 200)
        return response

    def post(self, action):
        """
        post: receive bind or unbind action from users
        :param action: command on the resource, which is specified on URL
        :return: [flask HTTP response in JSON] action acceptance result
        """
        # Bind action
        if action == "bind":
            return self.bind()

        # Unbind action
        elif action == "unbind":
            return self.unbind()

        # Reject other actions
        else:
            abort_json(400, "Invalid action.")

    @authentication_required
    def bind(self):
        # Read user id from HTTP request header
        user_id = request.headers.get('USER-ID')

        # Raise 409 Conflict error if the resource is already bound to another user
        if self.redis.exists('user_id') and self.redis.get('user_id') != user_id:
            abort_json(409, "Resource bound to another user.")

        # Bind user successfully
        else:
            self.redis.set('user_id', user_id)
            
            response = make_response(jsonify({
                "userId": self.redis.get('user_id')
            }), 200)
            return response

    @authorization_required
    def unbind(self):
        # Read user id from HTTP request header
        user_id = request.headers.get('USER-ID')

        # Raise 401 error if the resource is not bound
        if not self.redis.exists('user_id'):
            abort_json(401, "Resource not bound.")

        # Unbind user successfully
        else:
            user_id = self.redis.get('user_id')
            self.redis.delete('user_id')

            response = make_response(jsonify({
                "userId": user_id
            }), 200)
            return response

    @staticmethod
    def add_url_rule(_app):
        """
        add_url_rule: add urls to flask app automatically
        :param _app: flask app
        :return: None
        """
        view = BindAPI.as_view('bind_api')
        # Bind API View
        _app.add_url_rule('/', view_func=view, methods=['GET', ])
        _app.add_url_rule('/user/<action>', view_func=view, methods=['POST', ])


class ResourceAPI(API):
    """
    ResourceAPI: base API for controlling resources
    """

    @abstractmethod
    def get(self):
        """
        get: returns resource's status information
        :return: [flask HTTP response in JSON] resource's status information
        """

    @abstractmethod
    def post(self, action):
        """
        post: controller actions that controls connected resource
        :param action: command from the user
        :return: [flask HTTP response in JSON] action acceptance result
        """

    @staticmethod
    @abstractmethod
    def add_url_rule(_app):
        """
        add_url_rule: add urls to flask app automatically
        :param _app: flask app
        :return: None
        """


class ServiceAPI(API):
    """
    ServiceAPI: base API for controlling services
    """

    @abstractmethod
    def get(self):
        """
        get: returns service's status information
        :return: [flask HTTP response in JSON] service's status information
        """

    @abstractmethod
    def post(self, action):
        """
        post: perform service actions by controlling connected resource
        :param action: command from the user
        :return: [flask HTTP response in JSON] action acceptance result
        """

    @staticmethod
    @abstractmethod
    def add_url_rule(_app):
        """
        add_url_rule: add urls to flask app automatically
        :param _app: flask app
        :return: None
        """