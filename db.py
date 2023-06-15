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
            "id": self.id(),
            "username": self.username,
            "email": self.email,
            "favorite_locations": self.favorite_locations,
            "suggested_locations": [str(location_id) for location_id in self.suggested_locations],
            "rating": self.rating,
        }


class Location:
    name: str
    description: str
    images: list
    comments: list[ObjectId]
    location: list[int]
    rating: list[int]
    tags: list[int]
    owner_id: ObjectId

    def jsonify(self):
        return {
            "id": self.id(),
            "name": self.name,
            "description": self.description,
            "images": [str(_id) for _id in self.images],
            "comments": self.comments,
            "location": self.location,
            "rating": self.rating,
            "tags": self.tags,
            "owner_id": str(self.owner_id),
        }


class Comment:
    owner_id: ObjectId
    content: str
    rating: list[int]


class Image:
    content: bytes


db = DataBase("Test")
db.add_collection(User)
db.add_collection(Location)
db.add_collection(Comment)
db.add_collection(Image)
db.build()
