import typing

from pangloss_core_new.model_setup.setup_utils import (
    _get_all_subclasses,
    _get_concrete_node_classes,
)
from pangloss_core_new.models import BaseNode


def test_get_all_subclasses():
    class Thing(BaseNode):
        pass

    class ChildThing(Thing):
        pass

    assert _get_all_subclasses(Thing) == set([ChildThing])


def test_get_all_subclasses_with_abstract():
    class Thing(BaseNode):
        pass

    class MiddleThing(Thing):
        __abstract__ = True

    class ChildThing(MiddleThing):
        pass

    assert _get_all_subclasses(Thing) == set([ChildThing])


def test_get_concrete_node_classes():
    class Thing(BaseNode):
        pass

    class ChildThing(Thing):
        pass

    assert _get_concrete_node_classes(Thing, include_subclasses=True) == set(
        [Thing, ChildThing]
    )


def test_get_concrete_node_classes_with_union():
    class Cat(BaseNode):
        pass

    class TinyCat(Cat):
        pass

    class Dog(BaseNode):
        pass

    class TinyDog(Dog):
        pass

    class MilliDog(Dog):
        __abstract__ = True

    class PicoDog(MilliDog):
        pass

    assert _get_concrete_node_classes(
        typing.Union[Cat, Dog], include_subclasses=True
    ) == set([Cat, Dog, TinyCat, TinyDog, PicoDog])
