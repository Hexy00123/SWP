from flask import Flask, request, jsonify, make_response, send_file, render_template
import os
from config import CONNECTION_STRING
from models import db
from bson import ObjectId, errors
import json
import io


def arg_checker(*allowed_args):
    def wrapper(func):
        def decorated_function():
            params = dict(request.args)
            for id in ['id', 'owner_id']:
                if id in params:
                    try:
                        params[id] = ObjectId(params[id])
                    except errors.InvalidId:
                        return make_response(f'Wrong {id} value', 400)

            wrong_arguments = set(params.keys()).difference(set(allowed_args))
            if wrong_arguments:
                return make_response(f'Wrong arguments: {", ".join(wrong_arguments)}', 400)

            return func(**params)

        decorated_function.__name__ = func.__name__

        return decorated_function

    return wrapper


app = Flask(__name__)


@app.route('/', methods=['GET'])
def api_page():
    return "API page"


@app.route('/register', methods=['POST'])
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


@app.route('/auto', methods=['GET'])
@arg_checker('email', 'password_hash')
def authorisation(email, password_hash):
    response = db.User.get(email=email)
    if response is None:
        return make_response(jsonify({}), 204)

    if db.User.get(email=email).password_hash == password_hash:
        return make_response(jsonify({"id": response.id(),
                                      "email": response.email}), 200)
    return make_response(jsonify({}), 401)


@app.route('/user', methods=['GET', 'PUT'])
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


@app.route('/location', methods=['GET'])
@arg_checker('id')
def location_get(id):
    location = db.Location.get_by_id(id)
    if location:
        return make_response(location.jsonify(), 200)
    return make_response({}, 204)


@app.route('/location', methods=['POST'])
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


@app.route('/location', methods=['PUT'])
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

    return make_response({}, 200)


@app.route('/location', methods=['DELETE'])
@arg_checker('id')
def location_delete(id):
    if db.Location.get_by_id(id) is None:
        return make_response({}, 204)

    db.Location.remove_by_id(id)
    return make_response({}, 200)


@app.route('/nearest_locations', methods=['GET'])
@arg_checker('radius', 'coordinates')
def nearest_locations(radius, coordinates):
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

    radius = float(radius)
    user_location = list(map(float, coordinates.split(',')))
    return make_response(jsonify(list(map(lambda obj: obj.jsonify(), db.Location.find(
        location=lambda loc: calculate_distance(*loc, *user_location) < radius)))), 200)


@app.route('/image', methods=['GET'])
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


@app.route('/admin/users', methods=['GET'])
@arg_checker()
def admin_users():
    return make_response(jsonify([user.jsonify() for user in db.User.find()]))


@app.route('/admin/users/show', methods=['GET'])
@arg_checker()
def admin_users_show():
    return render_template('users.html', users=list(map(lambda us: us.jsonify(), db.User.find())))


@app.route('/admin/locations', methods=['GET'])
@arg_checker()
def admin_locations():
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]))


@app.route('/admin/locations/show', methods=['GET'])
@arg_checker()
def admin_locations_show():
    return render_template('locations.html', locations=list(map(lambda loc: loc.jsonify(), db.Location.find())))


@app.route('/admin/images', methods=['GET'])
@arg_checker()
def admin_images():
    return make_response(jsonify([image.id() for image in db.Image.find()]))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
