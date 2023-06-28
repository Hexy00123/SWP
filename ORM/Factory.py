from bson import ObjectId


class Factory:
    def __init__(self, dtype: type):
        self.dtype = dtype

    def create_inst(self, **kwargs):
        '''
        Description: Creates an instance of the data type with the provided keyword arguments.
        Parameters:
          - kwargs: Keyword arguments for initializing the instance.
        Returns:
          - The created instance.
        '''

        class Data(self.dtype):
            def __init__(obj, **kwargs):
                if kwargs:
                    obj._id = kwargs["_id"]
                    obj.__is_changed = False
                    del kwargs["_id"]
                    super().__init__(**kwargs)

            def id(obj):
                return str(obj._id)

            def pure_type(obj):
                return obj.__class__.mro()[1]

            def __str__(obj):
                return f"{str(self.dtype.__name__)}: {'{'}{', '.join([f'{field}={getattr(obj, field)}' for field in self.dtype.__annotations__])}{'}'}"

            def __repr__(obj):
                return obj.__str__()

            def jsonify(obj):
                def convert_to_json(value):
                    if isinstance(value, ObjectId):
                        return str(value)
                    elif isinstance(value, list):
                        return [convert_to_json(item) for item in value]
                    elif isinstance(value, dict):
                        return {key: convert_to_json(val) for key, val in value.items()}
                    elif isinstance(value, bytes):
                        raise TypeError("Objects with bytes field cannot be dumped to the JSON")
                    else:
                        return value

                result = {
                    'id': obj.id()
                }
                for field in self.dtype.__annotations__:
                    result[field] = convert_to_json(getattr(obj, field))

                return result

        if self.dtype.__init__ != object.__init__:
            inst = Data(**kwargs)
        else:
            inst = Data()
            for field in kwargs:
                setattr(inst, field, kwargs[field])
        return inst
