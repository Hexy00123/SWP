class Factory:
    def __init__(self, dtype: type):
        self.dtype = dtype

    def create_inst(self, **kwargs):
        class Data(self.dtype):
            def __init__(obj, **kwargs):
                if kwargs:
                    obj._id = kwargs["_id"]
                    obj.__is_changed = False
                    del kwargs["_id"]
                    super().__init__(**kwargs)

            def id(obj):
                return str(obj._id)

            def is_changed(obj):
                return self.__is_changed

            def __str__(obj):
                return f"{str(self.dtype.__name__)}: {'{'}{', '.join([f'{field}={getattr(obj, field)}' for field in self.dtype.__annotations__])}{'}'}"

            def __repr__(obj):
                return obj.__str__()

        if self.dtype.__init__ != object.__init__:
            inst = Data(**kwargs)
        else:
            inst = Data()
            for field in kwargs:
                setattr(inst, field, kwargs[field])
        return inst
