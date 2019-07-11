class SingletonMetaClass(type):
    """Singleton metaclass that defines how attributes are set."""

    def __setattr__(self, key, value):
        if key in self.__dict__:
            return super(SingletonMetaClass, self).__setattr__(key, value)
        else:
            for base_class in self.__bases__:
                if key in base_class.__dict__:
                    return setattr(base_class, key, value)
