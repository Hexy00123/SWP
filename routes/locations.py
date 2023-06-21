from routes.utils import arg_checker
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

locations_blueprint = Blueprint('locations', __name__)


@locations_blueprint.route('/location', methods=['GET'])
@arg_checker('id')
def location_get(id):
    location = db.Location.get_by_id(id)
    if location:
        return make_response(location.jsonify(), 200)
    return make_response({}, 204)


@locations_blueprint.route('/location', methods=['POST'])
@arg_checker('owner_id', 'name', 'description', 'tags', 'location')
def location_post(owner_id, name, description, tags, location):
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
@arg_checker('id', 'name', 'description', 'location', 'tags')
def location_put(id, name=None, description=None, location=None, tags=None):
    if db.Location.get_by_id(id) is None:
        return make_response(jsonify({}), 204)

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

    return make_response(jsonify(db.Location.get_by_id(id)), 200)


@locations_blueprint.route('/location', methods=['DELETE'])
@arg_checker('id')
def location_delete(id):
    if db.Location.get_by_id(id) is None:
        return make_response({}, 204)

    db.Location.remove_by_id(id)
    return make_response({}, 200)


@locations_blueprint.route('/nearest_locations', methods=['GET'])
@arg_checker('radius', 'coordinates')
def nearest_locations(radius, coordinates):
    from routes.utils import calculate_distance

    radius = float(radius)
    user_location = list(map(float, coordinates.split(',')))
    return make_response(jsonify(list(map(lambda obj: obj.jsonify(), db.Location.find(
        location=lambda loc: calculate_distance(*loc, *user_location) < radius)))), 200)


@locations_blueprint.route('/image', methods=['GET'])
@arg_checker('id')
def image(id):
    img = db.Image.get_by_id(id)
    if img is None:
        return make_response({}, 204)

    return send_file(
        io.BytesIO(img.content),
        mimetype='image/jpg',
        as_attachment=True,
        download_name=f'{request.args["id"]}.jpg')
