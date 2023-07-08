from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, request
from models import *

comment_blueprint = Blueprint('comments', __name__)


@comment_blueprint.route('/comment', methods=['POST'])
@validator('location_id', 'owner_id', 'content', 'password',
           validation_methods=[(user_authorisation, ('owner_id', 'password'))])
def create_comment(location_id, owner_id, content, password):
    """
    Create a new comment for a location.

    Args:
        location_id (str): ID of the location to add the comment to.
        owner_id (str): ID of the user creating the comment.
        content (str): Content of the comment.
        password (str): Password for user authorization.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    location, user = db.Location.get_by_id(location_id), db.User.get_by_id(owner_id)
    if location is None or user is None:
        return make_response({}, 204)
    _id = db.Comment.add(owner_id=owner_id, content=content, rating=[0, 0])
    location_comments = location.comments + [_id]
    db.Location.update_instance(location_id, 'comments', location_comments)

    return make_response({}, 201)


@comment_blueprint.route('/comment', methods=['GET'])
@validator('id')
def get_comment(id):
    """
    Get a comment by its ID.

    Args:
        id (str): ID of the comment to retrieve.

    Returns:
        Flask response: JSON response containing the comment object.
    """
    comment = db.Comment.get_by_id(id)
    user = db.User.get_by_id(comment.owner_id)
    if comment is None:
        return make_response({}, 204)
    response = comment.jsonify()
    if user:
        response['username'] = user.username
    else:
        response['username'] = 'deleted account'
    return make_response(jsonify(response), 200)
