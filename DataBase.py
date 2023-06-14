import pymongo
from bson import ObjectId
from typing import get_args, get_origin
from config import CONNECTION_STRING
from Factory import Factory


class DBCollection():
    def __init__(self, *_, dtype: type, db, db_collection):
        self.dtype = dtype
        self.db = db
        self.db_collection = db_collection
        self.factory = Factory(self.dtype)

    def add(self, *obj, **parameters) -> ObjectId:
        if obj and parameters:
            raise AttributeError(f"Method can accept object fields or template itself, not both.")

        fields = [attr for attr in self.dtype.__annotations__]
        db_object = {field: None for field in fields}

        if len(obj) == 1:
            obj = obj[0]
            if type(obj) != self.dtype:
                raise TypeError(
                    f"Type {type(obj).__name__} cannot be inserted to a collection with type {self.dtype.__name__}")

            for field in fields:
                try:
                    db_object[field] = obj.__dict__[field]
                except KeyError:
                    db_object[field] = None
        if parameters:
            for parameter in parameters:
                if parameter in fields:
                    db_object[parameter] = parameters[parameter]
                else:
                    raise AttributeError(f"Wrong attribute for the object of type {self.dtype.__name__}")

        print(f"{self.dtype.__name__}: {db_object}")
        return self.db_collection.insert_one(db_object).inserted_id

    def find(self, **kwargs):
        class SearchList(list):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def where(self, **kwargs):
                res = []
                for element in self:
                    satisfy = True

                    for parameter in kwargs:
                        if parameter in {"id", "_id"}:
                            if getattr(element, "_id") != kwargs[parameter]:
                                satisfy = False
                        elif kwargs[parameter] is None:
                            if getattr(element, parameter) is not None:
                                satisfy = False
                        elif getattr(element, parameter) is None:
                            satisfy = False
                        elif type(kwargs[parameter]) == type(lambda x: x):
                            if not kwargs[parameter](getattr(element, parameter)):
                                satisfy = False
                        elif getattr(element, parameter) != kwargs[parameter]:
                            satisfy = False
                    if satisfy:
                        res.append(element)
                return res

        res = SearchList()
        for obj in self.db_collection.find().__iter__():
            instance = self.factory.create_inst(**obj)
            res.append(instance)

        return res.where(**kwargs)

    def get(self, **kwargs):
        res = self.find(**kwargs)
        if len(res) == 0:
            return None
        return res[0]

    def get_by_id(self, id):
        res = self.db_collection.find_one({"_id": id})
        if res:
            return self.factory.create_inst(**res)
        return None


class DataBase():
    BASE_TYPES = [ObjectId, int, float, str, bool]
    ITERABLE_TYPES = [list, tuple, dict, set]

    @staticmethod
    def _check_type(dtype: type):
        if dtype in DataBase.BASE_TYPES:
            return

        if dtype in DataBase.ITERABLE_TYPES:
            return

        if get_origin(dtype) in DataBase.ITERABLE_TYPES:
            for nested in get_args(dtype):
                DataBase._check_type(nested)
        else:
            raise TypeError(f"Unknown type(s) for db: {dtype}")

    def __init__(self, name):
        self.client = pymongo.MongoClient(CONNECTION_STRING)
        self.db = self.client.get_database(name)
        self.dtypes = []
        self.collections = dict()

    def add_collection(self, dtype: type):
        if type(dtype) is not type:
            raise TypeError("Collection can accept only type")
        self.dtypes.append(dtype)

    def build(self):
        for dtype in self.dtypes:
            for field in dtype.__annotations__:
                DataBase._check_type(dtype.__annotations__[field])

        for dtype in self.dtypes:
            if dtype.__name__ not in self.db.list_collection_names():
                print(f"Creating collection: {dtype.__name__}")
                self.db.create_collection(dtype.__name__)
            self.collections[dtype.__name__] = DBCollection(dtype=dtype, db=self,
                                                            db_collection=self.db.get_collection(dtype.__name__))
            self.__dict__[dtype.__name__]: DBCollection = self.collections[dtype.__name__]
