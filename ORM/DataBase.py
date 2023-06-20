import pymongo
from bson import ObjectId
from typing import get_args, get_origin
from config import CONNECTION_STRING
from ORM.Factory import Factory


class DBCollection():
    def __init__(self, *_, dtype: type, db, db_collection):
        '''
        Description: A class representing a collection in the database.
        Parameters:
          - dtype: The data type associated with the collection.
          - db: The database instance.
          - db_collection: The collection instance in the database.
        '''
        self.dtype = dtype
        self.db = db
        self.db_collection = db_collection
        self.factory = Factory(self.dtype)

    def add(self, *obj, **parameters) -> ObjectId:
        '''
        Description: Adds a new object or object fields to the collection.
        Parameters:
          - obj: The object to be added to the collection.
          - parameters: Object fields to be added directly to the collection.
        Returns:
          - The ID of the inserted object.
        Raises:
          - AttributeError: If both obj and parameters are provided.
          - TypeError: If the provided object is not of the specified data type.
        '''
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

        return self.db_collection.insert_one(db_object).inserted_id

    def find(self, **kwargs):
        '''
        Description: Retrieves objects from the collection based on the provided criteria.
        Parameters:
          - kwargs: Criteria for filtering the objects.
                    Can also accept a lambda function, which returns bool
                    for advanced filtering.
        Returns:
          - A list of objects that satisfy the criteria.
        '''

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
        '''
        Description: Retrieves a single object from the collection based on the provided criteria.
        Parameters:
          - kwargs: Criteria for filtering the object.
        Returns:
          - One object that satisfies the criteria, or None if no object is found.
        '''
        res = self.find(**kwargs)
        if len(res) == 1:
            return res[0]
        elif len(res) == 0:
            return None
        return res[0]

    def get_by_id(self, id):
        '''
        Description: Retrieves an object from the collection based on its ID.
        Parameters:
          - id: The ID of the object.
        Returns:
          - The object with the specified ID, or None if no object is found.
        '''
        res = self.db_collection.find_one({"_id": id})
        if res:
            return self.factory.create_inst(**res)
        return None

    def remove_by_id(self, id):
        '''
        Description: Removes an object from the collection based on its ID.
        Parameters:
          - id: The ID of the object to be removed.
        '''
        self.db_collection.delete_many({"_id": {"$eq": id}})

    def update_instance(self, id, key, value):
        '''
        Description: Updates a specific field of an object in the collection.
        Parameters:
          - id: The ID of the object to be updated.
          - key: The field to be updated.
          - value: The new value for the field.
        '''
        self.db_collection.find_one_and_update({"_id": id}, {'$set': {key: value}})


class DataBase():
    BASE_TYPES = [ObjectId, int, float, str, bool, bytes]
    COMPOSE_TYPES = [list, tuple, dict, set]

    @staticmethod
    def _check_type(dtype: type):
        '''
        Description: Checks if the data type is supported by the database.
        Parameters:
          - dtype: The data type to be checked.
        Raises:
          - TypeError: If the data type is not supported.
        '''
        if dtype in DataBase.BASE_TYPES:
            return

        if dtype in DataBase.COMPOSE_TYPES:
            return

        if get_origin(dtype) in DataBase.COMPOSE_TYPES:
            for nested in get_args(dtype):
                DataBase._check_type(nested)
        else:
            raise TypeError(f"Unknown type(s) for db: {dtype}")

    def __init__(self, name, connection_string):
        '''
        # Description: Initializes a database instance.
        # Parameters:
        #   - name: The name of the database.
        '''
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.get_database(name)
        self.dtypes = []
        self.collections = dict()

    def add_collection(self, dtype: type):
        '''
        Description: Adds a collection to the database.
        Parameters:
          - dtype: The data type associated with the collection.
        Raises:
        - TypeError: If the provided dtype is not a type.
        '''
        if type(dtype) is not type:
            raise TypeError("Collection can accept only type")
        self.dtypes.append(dtype)

    def build(self):
        # Description: Builds the collections in the database.
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
