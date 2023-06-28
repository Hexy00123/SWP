from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *
import hashlib

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/register', methods=['POST'])
@validator('username', 'email', 'password')
def register(username, email, password):
    if db.User.get(email=email) is not None:
        return make_response(jsonify({}), 208)

    db.User.add(username=username,
                email=email,
                password_hash=hashlib.md5(password.encode()).hexdigest(),
                favorite_locations=[],
                suggested_locations=[],
                rating=[0, 0])

    return make_response(jsonify({}), 201)


@users_blueprint.route('/auto', methods=['GET'])
@validator('email', 'password')
def authorisation(email, password):
    response = db.User.get(email=email)
    if response is None:
        return make_response(jsonify({}), 204)

    if db.User.get(email=email).password_hash == hashlib.md5(password.encode()).hexdigest():
        return make_response(jsonify({"id": response.id(),
                                      "email": response.email}), 200)
    return make_response(jsonify({}), 401)


@users_blueprint.route('/user', methods=['GET'])
@validator('id')
def user_get(id):
    user = db.User.get_by_id(id)
    if user is None:
        return make_response(jsonify({}), 204)
    response = user.jsonify()
    del response['password_hash']
    return make_response(jsonify(response), 200)


@users_blueprint.route('/user', methods=['PUT'])
@validator('id', 'username', 'password',
           validation_methods=[(user_authorisation, ('id', 'password'))])
def change_username(id, username, password):
    user = db.User.get_by_id(id)
    if user is None:
        return make_response(jsonify({}), 204)
    db.User.update_instance(id=id, key='username', value=username)
    return make_response({}, 200)


@users_blueprint.route('/favorites', methods=['POST'])
@validator('id', 'location_id', 'password',
           validation_methods=[(user_authorisation, ('id', 'password'))])
def add_location_to_favorites(id, location_id, password):
    user = db.User.get_by_id(id)
    location = db.Location.get_by_id(location_id)

    if user is None or location is None:
        return make_response(jsonify({}), 204)

    if location_id in user.favorite_locations:
        return make_response(jsonify({}), 208)

    db.User.update_instance(id, 'favorite_locations', user.favorite_locations + [location_id])
    return make_response(jsonify({}), 201)


@users_blueprint.route('/favorites', methods=['DELETE'])
@validator('id', 'location_id', 'password',
           validation_methods=[(user_authorisation, ('id', 'password'))])
def remove_location_from_favorites(id, location_id, password):
    user = db.User.get_by_id(id)
    location = db.Location.get_by_id(location_id)

    if user is None or location is None:
        return make_response(jsonify({}), 204)

    if location_id not in user.favorite_locations:
        return make_response(jsonify({}), 204)

    user_favorites = user.favorite_locations
    user_favorites.remove(location_id)
    db.User.update_instance(id, 'favorite_locations', user_favorites)
    return make_response(jsonify({}), 201)
