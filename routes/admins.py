from routes.utils import arg_checker
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

admins_blueprint = Blueprint('admins', __name__)


@admins_blueprint.route('/admin/users', methods=['GET'])
@arg_checker()
def admin_users():
    return make_response(jsonify([user.jsonify() for user in db.User.find()]))


@admins_blueprint.route('/admin/users/show', methods=['GET'])
@arg_checker()
def admin_users_show():
    return render_template('users.html', users=list(map(lambda us: us.jsonify(), db.User.find())))


@admins_blueprint.route('/admin/users/clear', methods=['GET'])
@arg_checker()
def admin_users_delete():
    for user in db.User:
        db.User.remove_by_id(user._id)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/locations', methods=['GET'])
@arg_checker()
def admin_locations():
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]))


@admins_blueprint.route('/admin/locations/show', methods=['GET'])
@arg_checker()
def admin_locations_show():
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))


@admins_blueprint.route('/admin/locations/clear', methods=['GET'])
@arg_checker()
def admin_locations_delete():
    for loc in db.Location:
        db.Location.remove_by_id(loc._id)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/images', methods=['GET'])
@arg_checker()
def admin_images():
    return make_response(jsonify([image.id() for image in db.Image.find()]))


@admins_blueprint.route('/admin/images/clear', methods=['GET'])
@arg_checker()
def admin_images_delete():
    for img in db.Images:
        db.Image.remove_by_id(img._id)
    return make_response(jsonify({}), 200)


@admins_blueprint.route('/admin/db/clear')
@arg_checker()
def clear_database():
    for col in [db.User, db.Location, db.Image, db.Comment, db.Rating]:
        for item in col:
            col.remove_by_id(item._id)
    return make_response(jsonify({}), 200)
