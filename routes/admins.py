from routes.utils import validator
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

admins_blueprint = Blueprint('admins', __name__)


@admins_blueprint.route('/admin/users', methods=['GET'])
@validator()
def admin_users():
    return make_response(jsonify([user.jsonify() for user in db.User.find()]), 200)


@admins_blueprint.route('/admin/users/show', methods=['GET'])
@validator()
def admin_users_show():
    return render_template('users.html', users=list(map(lambda us: us.jsonify(), db.User.find())))


@admins_blueprint.route('/admin/user', methods=['DELETE'])
@validator('id')
def admin_users_delete(id):
    if db.User.get_by_id(id) is None:
        return make_response(jsonify({}), 204)
    db.User.remove_by_id(id)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/locations', methods=['GET'])
@validator()
def admin_locations():
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]), 200)


@admins_blueprint.route('/admin/locations/show', methods=['GET'])
@validator()
def admin_locations_show():
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))


@admins_blueprint.route('/admin/location', methods=['DELETE'])
@validator('id')
def admin_locations_delete(id):
    if db.Location.get_by_id(id) is None:
        return make_response(jsonify({}), 204)
    db.Location.remove_by_id(id)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/images', methods=['GET'])
@validator()
def admin_images():
    return make_response(jsonify([image.id() for image in db.Image.find()]), 200)


@admins_blueprint.route('/admin/image', methods=['DELETE'])
@validator('id')
def admin_images_delete(id):
    if db.Image.get_by_id(id) is None:
        return make_response(jsonify({}), 204)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/db', methods=['DELETE'])
@validator()
def clear_database():
    for col in [db.User, db.Location, db.Image, db.Comment, db.Rating]:
        for item in col:
            col.remove_by_id(item._id)
    return make_response(jsonify({}), 200)
