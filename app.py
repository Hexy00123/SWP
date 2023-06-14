from flask import Flask, request, jsonify, make_response
import os
from config import CONNECTION_STRING
from db import db
from bson import ObjectId

app = Flask(__name__)


@app.route('/', methods=['GET'])
def api_page():
    return "API page"


@app.route('/register', methods=["POST"])
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


@app.route('/auto', methods=["GET"])
def authorisation():
    email, password_hash = request.args["email"], request.args["password_hash"]
    response = db.User.get(email=email)
    if response is None:
        return make_response(jsonify({}), 204)

    if db.User.get(email=email).password_hash == password_hash:
        return make_response(jsonify({"id": response.id(),
                                      "email": response.email}), 200)
    return make_response(jsonify({}), 401)


@app.route('/user', methods=['GET'])
def get_user_data():
    parameters = dict(request.args)
    if "id" in parameters:
        parameters["_id"] = ObjectId(parameters["id"])
        del parameters["id"]

    print(parameters)
    user = db.User.get(**parameters)
    if user is not None:
        return make_response(jsonify(user.jsonify()), 200)
    return make_response(jsonify({}), 204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
