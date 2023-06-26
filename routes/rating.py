from routes.utils import validator, user_authorisation
from flask import Blueprint, make_response, jsonify, render_template, request
from models import *

rating_blueprint = Blueprint('rating', __name__)


@rating_blueprint.route('/rate', methods=['POST'])
@validator('user_id', 'object_id', 'is_positive', 'password',
           validation_methods=[(user_authorisation, {'user_id': 'owner_id', 'password': 'password'})])
def put_rating(user_id, object_id, is_positive, password):
    if is_positive.lower() == 'true':
        is_positive = True
    elif is_positive.lower() == 'false':
        is_positive = False
    else:
        return make_response({}, 400)

    user = db.User.get_by_id(user_id)
    if user is None:
        return make_response(jsonify({}), 204)

    obj = db.Location.get_by_id(object_id)
    if obj is not None:
        rating = db.Rating.find(user_id=user_id, object_id=object_id)
        if rating:
            rating = rating[0]
            if rating.is_positive == is_positive:
                return make_response(jsonify({}), 208)

            db.Rating.update_instance(rating._id, 'is_positive', is_positive)

            author = db.User.get_by_id(obj.owner_id)
            author_rating = author.rating
            author_rating[0 if is_positive else 1] += 1
            author_rating[0 if not is_positive else 1] -= 1
            db.User.update_instance(author._id, 'rating', author_rating)

            location_rating = obj.rating
            location_rating[0 if is_positive else 1] += 1
            location_rating[0 if not is_positive else 1] -= 1
            db.Location.update_instance(object_id, 'rating', location_rating)

            return make_response(jsonify({}), 201)

        db.Rating.add(user_id=user_id, object_id=object_id, is_positive=is_positive)

        author = db.User.get_by_id(obj.owner_id)
        author_rating = author.rating
        author_rating[0 if is_positive else 1] += 1
        db.User.update_instance(author._id, 'rating', author_rating)

        location_rating = obj.rating
        location_rating[0 if is_positive else 1] += 1
        db.Location.update_instance(object_id, 'rating', location_rating)

        return make_response(jsonify({}), 201)

    obj = db.Comment.get_by_id(object_id)
    if obj is not None:
        rating = db.Rating.find(user_id=user_id, object_id=object_id)
        if rating:
            rating = rating[0]
            if rating.is_positive == is_positive:
                return make_response(jsonify({}), 208)

            db.Rating.update_instance(rating._id, 'is_positive', is_positive)

            author = db.User.get_by_id(obj.owner_id)
            author_rating = author.rating
            author_rating[0 if is_positive else 1] += 1
            author_rating[0 if not is_positive else 1] -= 1
            db.User.update_instance(author._id, 'rating', author_rating)

            comment_rating = obj.rating
            comment_rating[0 if is_positive else 1] += 1
            comment_rating[0 if not is_positive else 1] -= 1
            db.Comment.update_instance(object_id, 'rating', comment_rating)

            return make_response(jsonify({}), 201)

        db.Rating.add(user_id=user_id, object_id=object_id, is_positive=is_positive)

        author = db.User.get_by_id(obj.owner_id)
        author_rating = author.rating
        author_rating[0 if is_positive else 1] += 1
        db.User.update_instance(author._id, 'rating', author_rating)

        comment_rating = obj.rating
        comment_rating[0 if is_positive else 1] += 1
        db.Comment.update_instance(object_id, 'rating', comment_rating)

        return make_response(jsonify({}), 201)

    return make_response({}, 204)
