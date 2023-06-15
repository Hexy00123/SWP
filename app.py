from flask import Flask, request, jsonify, make_response, send_file
import os
from config import CONNECTION_STRING
from db import db
from bson import ObjectId
import json
import io

app = Flask(__name__)


@app.route('/', methods=['GET'])
def api_page():
    return "API page"


@app.route('/register', methods=['POST'])
def registration():
    username, email, password_hash = request.args["username"], request.args["email"], request.args["password_hash"]

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
def authorisation():
    email, password_hash = request.args["email"], request.args["password_hash"]
    response = db.User.get(email=email)
    if response is None:
        return make_response(jsonify({}), 204)

    if db.User.get(email=email).password_hash == password_hash:
        return make_response(jsonify({"id": response.id(),
                                      "email": response.email}), 200)
    return make_response(jsonify({}), 401)


@app.route('/user', methods=['GET', 'PUT'])
def get_user_data():
    if request.method == 'GET':
        parameters = dict(request.args)
        if "id" in parameters:
            parameters["_id"] = ObjectId(parameters["id"])
            del parameters["id"]

        print(parameters)
        user = db.User.get(**parameters)
        if user is not None:
            return make_response(jsonify(user.jsonify()), 200)
        return make_response(jsonify({}), 204)
    elif request.method == 'PUT':
        parameters = dict(request.args)

        if "id" in parameters:
            parameters["_id"] = ObjectId(parameters["id"])
            del parameters["id"]

        user = db.User.get_by_id(parameters['_id'])
        if user is not None:
            user.update(username=parameters['username'])
            return make_response({}, 200)
        return make_response({}, 204)


@app.route('/location', methods=['GET', 'POST', 'PUT', 'DELETE'])
def location():
    if request.method == 'GET':
        _id = ObjectId(request.args['id'])
        location = db.Location.get_by_id(_id)
        if location:
            return make_response(location.jsonify(), 200)
        return make_response({}, 204)

    elif request.method == 'POST':
        owner_id = ObjectId(request.args["owner_id"])
        name = request.args["name"]
        description = request.args["description"]
        tags = list(map(int, request.args["tags"].strip().split(',')))
        print(request.args['tags'], tags)
        location = list(map(float, request.args["location"].strip().split(',')))

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

    elif request.method == 'PUT':
        _id = ObjectId(request.args['id'])
        location = db.Location.get_by_id(_id)
        if location is not None:
            params = dict(request.args)
            del params['id']

            for key in params:
                if key in {"name", "description"}:
                    db.Location.update_instance(_id, key, params[key])
                elif key == "location":
                    db.Location.update_instance(_id, key, list(map(float, params[key])))
                elif key == "tags":
                    db.Location.update_instance(_id, key, list(map(int, params[key])))
                else:
                    return make_response("not allowed", 404)

            if request.files:
                db.Location.update_instance(_id, "images",
                                            [db.Image.add(content=request.files[obj].read()) for obj in request.files])

            return make_response({}, 200)
        return make_response({}, 204)

    elif request.method == 'DELETE':
        _id = ObjectId(request.args['id'])
        if db.Location.get_by_id(_id) is not None:
            db.Location.remove_by_id(_id)
            return make_response({}, 200)
        return make_response({}, 204)


@app.route('/nearest_locations', methods=['GET'])
def nearest_locations():
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

    radius = float(request.args['radius'])
    user_location = list(map(float, request.args['coordinates'].split(',')))
    return make_response(jsonify(list(map(lambda obj: obj.jsonify(), db.Location.find(
        location=lambda loc: calculate_distance(*loc, *user_location) < radius)))), 200)


@app.route('/image', methods=['GET'])
def get_image():
    _id = ObjectId(request.args['id'])
    img = db.Image.get_by_id(_id)
    if img is not None:
        return send_file(
            io.BytesIO(img.content),
            mimetype='image/jpg',
            as_attachment=True,
            download_name=f'{request.args["id"]}.jpg')
    return make_response({}, 204)


@app.route('/admin/users', methods=['GET'])
def admin_get_all_users():
    return make_response(jsonify([user.jsonify() for user in db.User.find()]))


@app.route('/admin/locations', methods=['GET'])
def admin_get_all_locations():
    return make_response(jsonify([location.jsonify() for location in db.Location.find()]))


@app.route('/admin/images', methods=['GET'])
def admin_get_all_images():
    return make_response(jsonify([image.id() for image in db.Image.find()]))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
