from bson import ObjectId, errors
from flask import request, make_response
from inspect import signature
from models import db
import hashlib


class ValidationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_code = 400


def validator(*allowed_args: str, validation_methods: list[tuple[callable, tuple]] = None):
    def wrapper(func):
        def decorated_function():
            params = dict(request.args)
            for id in ['id', 'owner_id', 'user_id', 'object_id', 'location_id']:
                if id in params:
                    try:
                        params[id] = ObjectId(params[id])
                    except errors.InvalidId:
                        return make_response(f'Wrong {id} value', 400)

            wrong_arguments = set(params.keys()).difference(set(allowed_args))
            if wrong_arguments:
                return make_response(f'Wrong arguments: {", ".join(wrong_arguments)}\n'
                                     f'Allowed arguments: {", ".join(allowed_args)}', 400)

            missed_arguments = set(allowed_args).difference(params.keys())
            if missed_arguments:
                return make_response(f'missed arguments: {missed_arguments}', 400)

            if validation_methods:
                for method in validation_methods:
                    checker, arguments = method
                    args = []
                    for request_key in arguments:
                        args.append(params[request_key])

                    try:
                        print(args)
                        checker(*args)
                    except ValidationException as e:
                        print(str(e))
                        return make_response(str(e), e.return_code)

            return func(**params)

        decorated_function.__name__ = func.__name__

        return decorated_function

    return wrapper


def calculate_distance(longitude1, latitude1, longitude2, latitude2):
    from math import radians, cos, sin, atan2, sqrt
    radius = 6371000

    lon1, lat1, lon2, lat2 = map(radians, [longitude1, latitude1, longitude2, latitude2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = radius * c
    return distance


def user_authorisation(user_id, password):
    user = db.User.get_by_id(user_id)
    if user is not None:
        if user.password_hash == hashlib.md5(password.encode()).hexdigest():
            return

        err = ValidationException('Wrong password: authorisation is prohibited')
        err.return_code = 401
        raise err

    err = ValidationException('User does not exist')
    err.return_code = 204
    raise err
