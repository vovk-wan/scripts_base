from typing import Callable, Dict


class ScriptBase:
    BASE: Dict[str, Callable] = {}

    @classmethod
    def default(cls, *args, **kwargs):
        return {'error': 'no method'}

    @classmethod
    def add_foo(cls, foo: Callable) -> None:
        cls.BASE[foo.__name__] = foo

    @classmethod
    def __call__(cls, foo: str, *args, **kwargs):
        return cls.BASE.get(foo, cls.default)(*args, **kwargs)


BASE = ScriptBase()


def add_to_base(foo: callable) -> Callable:
    BASE.add_foo(foo)
    def wrapper(*args, **kwargs):
        return foo(*args, **kwargs)

    return wrapper


@add_to_base
def test1(*args, **kwargs) -> Dict:
    # some happened
    return {name: [args, value] for name, value in kwargs.items()}


if __name__ == '__main__':
    print(BASE('test1', 1, 2, 3, a=10, b=20))
