class SpiderFactory:
    _spiders = {}
    @classmethod
    def get(cls, spider_type:str):
        try:
            return cls._spiders[spider_type]()
        except KeyError:
            raise ValueError(f"Unknown Spider: {spider_type}")

    @classmethod
    def register(cls, spider_type:str):
        def inner_wrapper(wrapped_class):
            cls._spiders[spider_type] = wrapped_class
            return wrapped_class
        return inner_wrapper

from spiders import *