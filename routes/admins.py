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


@admins_blueprint.route('/admin/locations', methods=['GET'])
@arg_checker()
def admin_locations():
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]))


@admins_blueprint.route('/admin/locations/show', methods=['GET'])
@arg_checker()
def admin_locations_show():
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))


@admins_blueprint.route('/admin/images', methods=['GET'])
@arg_checker()
def admin_images():
    return make_response(jsonify([image.id() for image in db.Image.find()]))
