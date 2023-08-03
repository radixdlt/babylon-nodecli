class BaseConfig:
    def __init__(self, settings: dict):
        if settings is not None:
            for key, value in settings.items():
                setattr(self, key, value)

    def __repr__(self):
        return repr(vars(self))

    def __iter__(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        for attr, value in class_variables.items():
            if self.__getattribute__(attr):
                yield attr, self.__getattribute__(attr)

    def to_dict(self):
        class_variables = {key: value
                           for key, value in self.__class__.__dict__.items()
                           if not key.startswith('__') and not callable(value)}
        returning_dict = dict(self)
        for attr, value in class_variables.items():
            if type(self.__getattribute__(attr)) not in (str, int, bool, dict) and self.__getattribute__(
                    attr) is not None:
                returning_dict[attr] = self.__getattribute__(attr).to_dict()
        return returning_dict


class SetupMode:
    _instance = None
    mode = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
