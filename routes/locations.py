from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, render_template, request, send_file
from models import *
import io

locations_blueprint = Blueprint('locations', __name__)


@locations_blueprint.route('/location', methods=['GET'])
@validator('id')
def location_get(id):
    """
    Get a location by its ID.

    Args:
        id (str): ID of the location to retrieve.

    Returns:
        Flask response: JSON response containing the location object.
    """
    location = db.Location.get_by_id(id)
    if location:
        return make_response(location.jsonify(), 200)
    return make_response({}, 204)


@locations_blueprint.route('/location', methods=['POST'])
@validator('owner_id', 'name', 'description', 'tags', 'location', 'password',
           validation_methods=[(user_authorisation, ('owner_id', 'password'))])
def location_post(owner_id, name, description, tags, location, password):
    """
    Create a new location.

    Args:
        owner_id (str): ID of the user creating the location.
        name (str): Name of the location.
        description (str): Description of the location.
        tags (str): Comma-separated tags associated with the location.
        location (str): Latitude and longitude coordinates of the location.
        password (str): Password for user authorization.

    Returns:
        Flask response: JSON response containing the created location object.
    """
    tags = list(map(int, tags.strip().split(',')))
    location = list(map(float, location.strip().split(',')))

    _id = db.Location.add(name=name,
                          description=description,
                          images=[db.Image.add(content=request.files[obj].read()) for obj in request.files],
                          comments=[],
                          location=location,
                          rating=[0, 0],
                          tags=tags,
                          owner_id=owner_id)

    db.User.update_instance(owner_id, 'suggested_locations',
                            db.User.get_by_id(owner_id).suggested_locations + [_id])

    return make_response(jsonify(db.Location.get_by_id(_id).jsonify()), 201)


@locations_blueprint.route('/location', methods=['PUT'])
@validator('id', 'name', 'description', 'location', 'tags')
def location_put(id, name=None, description=None, location=None, tags=None):
    """
    Update an existing location.

    Args:
        id (str): ID of the location to update.
        name (str, optional): New name of the location. Defaults to None.
        description (str, optional): New description of the location. Defaults to None.
        location (str, optional): New latitude and longitude coordinates of the location. Defaults to None.
        tags (str, optional): New comma-separated tags associated with the location. Defaults to None.

    Returns:
        Flask response: JSON response containing the updated location object.
    """
    if db.Location.get_by_id(id) is None:
        return make_response({}, 204)

    if name:
        db.Location.update_instance(id, 'name', name)
    if description:
        db.Location.update_instance(id, 'description', description)
    if location:
        db.Location.update_instance(id, 'location', list(map(float, location.split(','))))
    if tags:
        db.Location.update_instance(id, 'tags', list(map(int, tags.split(','))))

    if request.files:
        db.Location.update_instance(id, "images",
                                    [db.Image.add(content=request.files[obj].read()) for obj in request.files])

    return make_response(jsonify(db.Location.get_by_id(id).jsonify()), 200)


@locations_blueprint.route('/location', methods=['DELETE'])
@validator('id')
def location_delete(id):
    """
    Delete a location by its ID.

    Args:
        id (str): ID of the location to delete.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    if db.Location.get_by_id(id) is None:
        return make_response({}, 204)

    db.Location.remove_by_id(id)
    return make_response({}, 200)


@locations_blueprint.route('/nearest_locations', methods=['GET'])
@validator('radius', 'coordinates')
def nearest_locations(radius, coordinates):
    """
    Get a list of locations within a certain radius of given coordinates.

    Args:
        radius (str): Radius in kilometers.
        coordinates (str): Latitude and longitude coordinates.

    Returns:
        Flask response: JSON response containing a list of nearby location objects.
    """
    from routes.utils import calculate_distance

    radius = float(radius)
    user_location = list(map(float, coordinates.split(',')))
    return make_response(jsonify(list(map(lambda obj: obj.jsonify(), db.Location.find(
        location=lambda loc: calculate_distance(*loc, *user_location) < radius)))), 200)


@locations_blueprint.route('/image', methods=['GET'])
@validator('id')
def image(id):
    """
    Get an image by its ID.

    Args:
        id (str): ID of the image to retrieve.

    Returns:
        Flask response: Image file with appropriate headers.
    """
    img = db.Image.get_by_id(id)
    if img is None:
        return make_response({}, 204)

    return send_file(
        io.BytesIO(img.content),
        mimetype='image/jpg',
        as_attachment=True,
        download_name=f'{request.args["id"]}.jpg')
