from DataBase import *


class User:
    username: str
    email: str
    password_hash: int
    favorite_locations: list[ObjectId]
    suggested_locations: list[ObjectId]
    rating: list[int]

    def jsonify(self):
        return {
            "username": self.username,
            "email": self.email,
            "favorite_locations": self.favorite_locations,
            "suggested_locations": self.suggested_locations,
            "rating": self.rating,
        }


class Location:
    name: str
    description: str
    images: list
    comments: list[ObjectId]
    geolocation: list[int]
    rating: list[int]
    tags: list[int]
    owner_id: ObjectId


class Comment:
    owner_id: ObjectId
    content: str
    rating: list[int]


db = DataBase("Test")
db.add_collection(User)
db.add_collection(Location)
db.add_collection(Comment)
db.build()
