from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, request
from models import *

comment_blueprint = Blueprint('comments', __name__)


@comment_blueprint.route('/comment', methods=['POST'])
@validator('location_id', 'owner_id', 'content', 'password',
           validation_methods=[(user_authorisation, ('owner_id', 'password'))])
def create_comment(location_id, owner_id, content, password):
    location, user = db.Location.get_by_id(location_id), db.User.get_by_id(owner_id)
    if location is None or user is None:
        return make_response(jsonify({}), 204)
    _id = db.Comment.add(owner_id=owner_id, content=content, rating=[0, 0])
    location_comments = location.comments + [_id]
    db.Location.update_instance(location_id, 'comments', location_comments)

    return make_response(jsonify({}), 201)


@comment_blueprint.route('/comment', methods=['GET'])
@validator('id')
def get_comment(id):
    comment = db.Comment.get_by_id(id)
    if comment is None:
        return make_response(jsonify({}), 204)
    return make_response(jsonify(comment.jsonify()), 200)
