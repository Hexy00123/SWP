from routes.utils import arg_checker
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/register', methods=['POST'])
@arg_checker('username', 'email', 'password_hash')
def register(username, email, password_hash):
    if db.User.get(email=email) is not None:
        return make_response(jsonify({}), 208)

    db.User.add(username=username,
                email=email,
                password_hash=password_hash,
                favorite_locations=[],
                suggested_locations=[],
                rating=[0, 0])

    return make_response(jsonify({}), 201)


@users_blueprint.route('/auto', methods=['GET'])
@arg_checker('email', 'password_hash')
def authorisation(email, password_hash):
    response = db.User.get(email=email)
    if response is None:
        return make_response(jsonify({}), 204)

    if db.User.get(email=email).password_hash == password_hash:
        return make_response(jsonify({"id": response.id(),
                                      "email": response.email}), 200)
    return make_response(jsonify({}), 401)


@users_blueprint.route('/user', methods=['GET', 'PUT'])
@arg_checker('id', 'username')
def user_route(id, username=None):
    user = db.User.get_by_id(id)
    if user is None:
        return make_response(jsonify({}), 204)

    if request.method == 'GET':
        return make_response(jsonify(user.jsonify()), 200)

    elif request.method == 'PUT':
        db.User.update_instance(id=id, key='username', value=username)
        return make_response({}, 200)
