from bson import ObjectId, errors
from flask import request, make_response


def arg_checker(*allowed_args):
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

            try:
                res = func(**params)
            except TypeError as e:
                text = str(e).split('positional arguments:')[1]
                return make_response(f'missed arguments: {text}', 400)

            return res

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
