from ORM.DataBase import *

db = DataBase("WebApplication", CONNECTION_STRING)


class User:
    """
    User model representing a user in the web application.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password_hash (int): The hash of the user's password.
        favorite_locations (list[ObjectId]): A list of favorite location IDs associated with the user.
        suggested_locations (list[ObjectId]): A list of suggested location IDs associated with the user.
        rating (list[int]): A list of ratings given by the user.
    """
    username: str
    email: str
    password_hash: int
    favorite_locations: list[ObjectId]
    suggested_locations: list[ObjectId]
    rating: list[int]


class Location:
    """
    Location model representing a location in the web application.

    Attributes:
        name (str): The name of the location.
        description (str): The description of the location.
        images (list): A list of images associated with the location.
        comments (list[ObjectId]): A list of comment IDs associated with the location.
        location (list[int]): The coordinates of the location.
        rating (list[int]): A list of ratings given to the location.
        tags (list[int]): A list of tags associated with the location.
        owner_id (ObjectId): The ID of the owner of the location.
    """
    name: str
    description: str
    images: list
    comments: list[ObjectId]
    location: list[int]
    rating: list[int]
    tags: list[int]
    owner_id: ObjectId


class Comment:
    """
    Comment model representing a comment in the web application.

    Attributes:
        owner_id (ObjectId): The ID of the comment owner.
        content (str): The content of the comment.
        rating (list[int]): A list of ratings given to the comment.
    """
    owner_id: ObjectId
    content: str
    rating: list[int]


class Image:
    """
    Image model representing an image in the web application.

    Attributes:
        content (bytes): The content of the image.
    """
    content: bytes


class Rating:
    """
    Rating model representing a rating in the web application.

    Attributes:
        user_id (ObjectId): The ID of the user giving the rating.
        object_id (ObjectId): The ID of the object being rated.
        is_positive (bool): Indicates if the rating is positive or not.
    """
    user_id: ObjectId
    object_id: ObjectId
    is_positive: bool


class Moderator:
    username: str
    password_hash: str


db.add_collection(User)
db.add_collection(Location)
db.add_collection(Comment)
db.add_collection(Image)
db.add_collection(Rating)
db.add_collection(Moderator)
db.build()
