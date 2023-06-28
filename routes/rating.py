from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

rating_blueprint = Blueprint('rating', __name__)


@rating_blueprint.route('/rate', methods=['POST'])
@validator('user_id', 'object_id', 'is_positive', 'password',
           validation_methods=[(user_authorisation, ('user_id', 'password'))])
def rate_object(user_id, object_id, is_positive, password):
    """
    Add or update a rating for an object (location or comment).

    Args:
        user_id (str): ID of the user giving the rating.
        object_id (str): ID of the object (location or comment) being rated.
        is_positive (str): Indicates whether the rating is positive or negative.
        password (str): Password for user authorization.

    Returns:
        Flask response: Empty response with status code indicating success or failure.
    """
    if is_positive.lower() not in ('true', 'false'):
        return make_response({}, 400)
    is_positive = is_positive == 'true'

    user = db.User.get_by_id(user_id)
    if user is None:
        return make_response({}, 204)

    obj = db.Location.get_by_id(object_id) or db.Comment.get_by_id(object_id)
    if obj is None:
        return make_response({}, 204)

    rating = db.Rating.find(user_id=user_id, object_id=object_id)
    if rating:
        rating = rating[0]
        if rating.is_positive == is_positive:
            return make_response({}, 208)

        db.Rating.update_instance(rating._id, 'is_positive', is_positive)

        author = db.User.get_by_id(obj.owner_id)
        author_rating = author.rating
        author_rating[0 if is_positive else 1] += 1
        author_rating[0 if not is_positive else 1] -= 1
        db.User.update_instance(author._id, 'rating', author_rating)

    else:
        db.Rating.add(user_id=user_id, object_id=object_id, is_positive=is_positive)

        author = db.User.get_by_id(obj.owner_id)
        author_rating = author.rating
        author_rating[0 if is_positive else 1] += 1
        db.User.update_instance(author._id, 'rating', author_rating)

    obj_rating = obj.rating
    obj_rating[0 if is_positive else 1] += 1
    if rating:
        obj_rating[0 if not is_positive else 1] -= 1

    if obj.pure_type() == Location:
        db.Location.update_instance(object_id, 'rating', obj_rating)
    elif obj.pure_type() == Comment:
        db.Comment.update_instance(object_id, 'rating', obj_rating)

    return make_response({}, 201)
