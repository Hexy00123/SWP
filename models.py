from ORM.DataBase import *

db = DataBase("WebApplication")


class User:
    username: str
    email: str
    password_hash: int
    favorite_locations: list[ObjectId]
    suggested_locations: list[ObjectId]
    rating: list[int]


class Location:
    name: str
    description: str
    images: list
    comments: list[ObjectId]
    location: list[int]
    rating: list[int]
    tags: list[int]
    owner_id: ObjectId


class Comment:
    owner_id: ObjectId
    content: str
    rating: list[int]


class Image:
    content: bytes


db.add_collection(User)
db.add_collection(Location)
db.add_collection(Comment)
db.add_collection(Image)
db.build()
