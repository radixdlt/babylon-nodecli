import yaml


class BaseConfig:
    def __init__(self, config_dict: dict):
        if config_dict is not None:
            for key, value in config_dict.items():
                setattr(self, key, value)

            class_variables = {key: value
                               for key, value in self.__class__.__dict__.items()
                               if not key.startswith('__') and not callable(value)}
            for attr, value in class_variables.items():
                if type(self.__getattribute__(attr)) not in (str, int, bool, dict) and self.__getattribute__(
                        attr) is not None:
                    if (config_dict.get(attr) is not None):
                        self.__getattribute__(attr).__init__(config_dict[attr])

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

    def to_yaml(self):
        config_to_dump = self.to_dict()
        return yaml.dump(config_to_dump, sort_keys=True, default_flow_style=False, explicit_start=True,
                         allow_unicode=True)

    def to_file(self, config_file):
        config_to_dump = self.to_dict()
        with open(config_file, 'w') as f:
            yaml.dump(config_to_dump, f, sort_keys=True, default_flow_style=False)


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
