"""
    Basic resource-controller classes for WebEng IoT testbed project

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
from functools import wraps
from flask import abort, request, jsonify
from flask.views import MethodView


def authentication_required(f):
    """
    authentication_required: a decorator to check authentication of requests
    :param f: original function to decorate
    :return: authentication function as a decorator
    """
    @wraps(f)
    def check_authentication(self, *args, **kwargs):
        # Every HTTP request should contain 'USER-ID' header
        user_id = request.headers.get('USER-ID')

        # Raise 401 Unauthorized error if user id is not set
        if user_id is None:
            abort(401, description="User ID not authenticated")

        # Finish the remaining process
        return f(self, *args, **kwargs)
    return check_authentication


def authorization_required(f):
    """
    authorization_required: a decorator to check authorization of requests according to bound status
    :param f: original function to decorate
    :return: authorization function as a decorator
    """
    @wraps(f)
    @authentication_required
    def check_authorization(self, *args, **kwargs):
        user_id = request.headers.get('USER-ID')

        # self.redis should be redis client
        assert isinstance(self.redis, redis.client.Redis)

        # Raise 409 Conflict error if the resource is already bound to another user
        if not self.redis.exists('user_id') or self.redis.get('user_id') != user_id:
            abort(409, description="Resource bound to another user")

        return f(self, *args, **kwargs)
    return check_authorization


class BindAPI(MethodView):
    """
    BindAPI: API for bind/unbind user to the resource.
    After a user is bound to the resource, the user becomes the owner of the resource until unbound himself/herself
    """
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def get(self):
        """
        get: responses currently bound user's ID
        :return: [flask HTTP response in JSON] bound user's ID
        """
        data = {
            "bound": self.redis.exists('user_id'),
            "user_id": self.redis.get('user_id')
        }
        return jsonify(data), 200  # TODO response body

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
            abort(400, description="Invalid action")

    @authentication_required
    def bind(self):
        # Read user id from HTTP request header
        user_id = request.headers.get('USER-ID')

        # Raise 409 Conflict error if the resource is already bound to another user
        if self.redis.exists('user_id') and self.redis.get('user_id') != user_id:
            abort(409, description="Resource bound to another user")

        # Bind user successfully
        else:
            self.redis.set('user_id', user_id)
            return 'User#%s is bound.' % user_id, 200  # TODO response body

    @authorization_required
    def unbind(self):
        # Read user id from HTTP request header
        user_id = request.headers.get('USER-ID')

        # Raise 400 Bad Request error if no one is bound
        if not self.redis.exists('user_id'):
            abort(400, description="No one bound")

        # Unbind user successfully
        else:
            self.redis.delete('user_id')
            return 'User#%s is unbound.' % user_id, 200  # TODO response body

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


class ResourceAPI(MethodView):
    """
    ResourceAPI: base API for controlling resources
    """
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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

