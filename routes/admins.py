from routes.utils import validator
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

admins_blueprint = Blueprint('admins', __name__)


@admins_blueprint.route('/admin/users', methods=['GET'])
@validator()
def admin_users():
    """
    Retrieve all users.

    Returns:
        Flask response: JSON response containing a list of user objects.
    """
    return make_response(jsonify([user.jsonify() for user in db.User.find()]), 200)


@admins_blueprint.route('/admin/users/show', methods=['GET'])
@validator()
def admin_users_show():
    """
    Render a template to display all users.

    Returns:
        Flask response: Rendered HTML template.
    """
    return render_template('users.html', users=list(map(lambda us: us.jsonify(), db.User.find())))


@admins_blueprint.route('/admin/user', methods=['DELETE'])
@validator('id')
def admin_users_delete(id):
    """
    Delete a user by ID.

    Args:
        id (str): ID of the user to be deleted.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    if db.User.get_by_id(id) is None:
        return make_response({}, 204)
    db.User.remove_by_id(id)
    return make_response({}, 200)


@admins_blueprint.route('/admin/locations', methods=['GET'])
@validator()
def admin_locations():
    """
    Retrieve all locations.

    Returns:
        Flask response: JSON response containing a list of location objects.
    """
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]), 200)


@admins_blueprint.route('/admin/locations/show', methods=['GET'])
@validator()
def admin_locations_show():
    """
    Render a template to display all locations.

    Returns:
        Flask response: Rendered HTML template.
    """
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))


@admins_blueprint.route('/admin/location', methods=['DELETE'])
@validator('id')
def admin_locations_delete(id):
    """
    Delete a location by ID.

    Args:
        id (str): ID of the location to be deleted.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    if db.Location.get_by_id(id) is None:
        return make_response({}, 204)
    db.Location.remove_by_id(id)
    return make_response({}, 200)


@admins_blueprint.route('/admin/images', methods=['GET'])
@validator()
def admin_images():
    """
    Retrieve all images.

    Returns:
        Flask response: JSON response containing a list of image IDs.
    """
    return make_response(jsonify([image.id() for image in db.Image.find()]), 200)


@admins_blueprint.route('/admin/image', methods=['DELETE'])
@validator('id')
def admin_images_delete(id):
    """
    Delete an image by ID.

    Args:
        id (str): ID of the image to be deleted.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    if db.Image.get_by_id(id) is None:
        return make_response({}, 204)
    return make_response({}, 200)


@admins_blueprint.route('/admin/db', methods=['DELETE'])
@validator()
def clear_database():
    """
    Clear the entire database.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    for col in [db.User, db.Location, db.Image, db.Comment, db.Rating]:
        for item in col:
            col.remove_by_id(item._id)
    return make_response({}, 200)
