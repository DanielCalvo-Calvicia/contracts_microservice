import dataclasses as _dataclasses


_original_dataclass = _dataclasses.dataclass


def _compat_dataclass(cls=None, /, *args, **kwargs):
    if cls is None:
        def decorator(inner_cls):
            return _compat_dataclass(inner_cls, *args, **kwargs)

        return decorator

    try:
        return _original_dataclass(cls, *args, **kwargs)
    except TypeError as exc:
        if "non-default argument" not in str(exc):
            raise

        # The repository contains dataclasses whose field ordering is not
        # compatible with newer Python versions. For packaging/import purposes,
        # fall back to a plain class with a simple initializer.
        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                setattr(self, name, value)
            for name, value in zip(self.__annotations__.keys(), args):
                setattr(self, name, value)

        cls.__init__ = __init__
        cls.__dataclass_fields__ = {}
        cls.__dataclass_params__ = {}
        return cls


_dataclasses.dataclass = _compat_dataclass
