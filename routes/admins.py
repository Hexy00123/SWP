from flask import jsonify, make_response, Blueprint, render_template, send_file
import hashlib
from models import *
from routes.utils import validator
import base64

admins_blueprint = Blueprint('admins', __name__)


@admins_blueprint.route('/admin/authorisation', methods=['GET'])
@validator('username', 'password')
def admin_authorisation(username, password):
    """
    Perform admin authorization.

    Args:
        username (str): The username of the admin.
        password (str): The password of the admin.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """

    moderator = db.Moderator.get(username=username)
    if moderator is None:
        return make_response({}, 204)
    if moderator.password_hash == hashlib.md5(password.encode()).hexdigest():
        return make_response({}, 200)
    return make_response({}, 401)


@admins_blueprint.route('/admin/users', methods=['GET'])
@validator()
def admin_users():
    """
    Retrieve all users.

    Returns:
        Flask response: JSON response containing a list of user objects.
    """
    return make_response(jsonify([user.jsonify() for user in db.User.find()]), 200)


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


@admins_blueprint.route('/admin', methods=['GET'])
@validator()
def admin_main():
    """
    Render the admin authorization template.

    Returns:
        Flask response: Rendered HTML template.
    """
    return render_template('adminautho.html')


@admins_blueprint.route('/admin/users/show', methods=['GET'])
@validator()
def admin_users_show():
    """
    Render a template to display all users.

    Returns:
        Flask response: Rendered HTML template.
    """
    return render_template('users.html', users=list(map(lambda us: us.jsonify(), db.User.find())))


@admins_blueprint.route('/admin/location/<location_id>', methods=['GET'])
def admin_location(location_id):
    """
    Render the template to display a specific location.

    Args:
        location_id (str): ID of the location to be displayed.

    Returns:
        Flask response: Rendered HTML template.
    """

    location = db.Location.get_by_id(ObjectId(location_id))

    images = [db.Image.get_by_id(img) for img in location.images]
    for image in images:
        image.content = base64.b64encode(image.content).decode('utf-8')

    return render_template('location_card.html',
                           location=location,
                           location_str = str(location.location[0])+','+str(location.location[1]),
                           comments=[db.Comment.get_by_id(comment).jsonify() for comment in location.comments],
                           images=images
                           )


@admins_blueprint.route('/admin/locations/show', methods=['GET'])
@validator()
def admin_locations_show():
    """
    Render a template to display all locations.

    Returns:
        Flask response: Rendered HTML template.
    """
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))
