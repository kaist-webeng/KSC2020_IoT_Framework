import requests
import json

from urllib.parse import urljoin
from functools import wraps
from flask import abort, request, jsonify, make_response


def abort_json(status_code, error_message):
    response = make_response(jsonify({
        "errorMessage": error_message
    }), status_code)
    abort(response)


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
            abort_json(401, "Authentication Failed.")

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

        # Raise 401 error if the resource is not bound
        if not self.redis.exists('user_id'):
            abort_json(401, "Resource not bound.")

        # Raise 409 Conflict error if the resource is already bound to another user
        if self.redis.get('user_id') != user_id:
            abort_json(409, "Resource bound to another user.")

        return f(self, *args, **kwargs)
    return check_authorization


def resource_required(resource_description):
    """
    resource_required: a decorator to indicate required resources for the action
    :param resource_description: url of required resource
    :return: resource binding function as a decorator
    """
    # TODO currently, allow single resource only: extend to multiple resources
    # TODO currently, directly specify url of the required resource: extend to use registry and discovery
    def decorator(f):
        @wraps(f)
        def bind_resource(self, *args, **kwargs):
            # TODO how to pass resource information to service?
            url = resource_description["url"]

            # Use the service's user id to control resources
            user_id = self.redis.get('user_id')
            headers = {'USER-ID': user_id}

            # Bind the resource
            bind_response = requests.post(url=urljoin(base=url, url='user/bind'),
                                          headers=headers)

            if bind_response.status_code == 200:
                # Binding successful

                resource = {
                    "name": resource_description["name"],
                    "url": resource_description["name"]
                }

                # Service action
                result = f(self, resource, *args, **kwargs)

                # Unbind the resource
                unbind_response = requests.post(url=urljoin(base=url, url='user/unbind'),
                                                headers=headers)

                return result
            else:
                # Binding failed
                # TODO error code
                abort_json(409, "Resource bound to another user.")
        return bind_resource
    return decorator


def register_api(identification, title, description):
    """
    register_api: a decorator for decorating API to construct description and register automatically
    :param identification: ID string of the API
    :param title: title of the API
    :param description: description of the API
    :return:
    """
    def decorator(cls):
        api_dict = {
            "@context": [
                "https://www.w3.org/2019/wot/td/v1",
                {"@language": "en"}
            ],
            "id": identification,
            "title": title,
            "description": description,
            "properties": {},
            "actions": {}
        }
        for obj in vars(cls).values():
            if callable(obj):
                if hasattr(obj, "__property"):
                    api_dict["properties"].update(getattr(obj, "__property"))
                if hasattr(obj, "__action"):
                    api_dict["actions"].update(getattr(obj, "__action"))
        cls.description = json.dumps(api_dict, indent=4)
        # TODO register the description to registry

        return cls

    return decorator


def add_property(name, title, description, properties, url, security="basic_sc"):
    """
    add_property: a decorator that add a property for API, based on WoT things format
    :param name: name of the property
    :param title: title of the property
    :param description: human-readable short description of the property
    :param properties: sub-properties of the property
    :param url: url to get the information of the property
    :param security: authorization level of the property
    :return: None
    """
    def decorator(f):
        property_dict = {
            name: {
                "title": title,
                "type": "object",
                "description": description,
                "properties": properties,
                "required": list(properties.keys()),
                "forms": [{
                    "href": url,
                    "htv:methodName": "GET",  # Assume every property is GET
                    "security": security
                }]
            }
        }
        f.__property = property_dict
        return f
    return decorator


def add_action(name, title, description, output, url, security="basic_sc"):
    """
    add_action: a decorator that add an action for API, based on WoT things format
    :param name: name of the action
    :param title: title of the action
    :param description: human-readable short description of the action
    :param output: a dictionary for the output properties of the action
    :param url: url to get the information of the action
    :param security: authorization level of the action
    :return: None
    """
    def decorator(f):
        action_dict = {
            name: {
                "title": title,
                "type": "object",
                "description": description,
                "output": {
                    "type": "object",
                    "properties": output
                },
                "required": [list(output.keys())],
                "forms": [{
                    "href": url,
                    "htv:methodName": "POST",  # Assume every action is POST
                    "security": security
                }]
            }
        }
        f.__action = action_dict
        return f
    return decorator


def logger(f):
    """
    logger: a decorator to enable logging to a method
    :param f: original function to decorate
    :return: function with logger attached
    """
    @wraps(f)
    def log(self, *args, **kwargs):

        # TODO currently, simple rest API is provided to collect raw data
        url = "http://143.248.47.96:8000/api/data/"

        # Get user ID
        user_id = self.redis.get('user_id')

        # Action
        result = f(self, *args, **kwargs)

        data = {
            "device_id": "Dummy",  # TODO
            "user_id": str(user_id),
            "function_name": f.__name__,
            "function_argument": str(args) + str(kwargs),
            "function_result": str(result)
        }

        requests.post(url=url, data=data)

        return result
    return log
