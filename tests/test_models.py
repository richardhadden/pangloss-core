from __future__ import annotations

import typing
import uuid

import annotated_types
import pytest

from pangloss_core_new.exceptions import PanglossConfigError
from pangloss_core_new.model_setup.base_node_definitions import (
    BaseNonHeritableMixin,
)
from pangloss_core_new.model_setup.config_definitions import (
    EmbeddedConfig,
    RelationConfig,
)
from pangloss_core_new.model_setup.relation_properties_model import (
    RelationPropertiesModel,
)
from pangloss_core_new.model_setup.embedded import Embedded
from pangloss_core_new.model_setup.model_manager import ModelManager
from pangloss_core_new.model_setup.relation_to import (
    RelationTo,
    ReifiedRelation,
    ReifiedTargetConfig,
)
from pangloss_core_new.models import BaseNode


@pytest.fixture(scope="function", autouse=True)
def reset_model_manager():
    ModelManager._reset()


def test_get_labels():
    class Thing(BaseNode):
        __abstract__ = True

    class Animal(Thing):
        pass

    class Pet(Animal):
        __abstract__ = True

    assert set(Pet._get_model_labels()) == set(["Thing", "Animal", "Pet", "BaseNode"])


def test_model_init_from_camel_dict():
    """Tests that models can be populated by the equivalent camelCase (standard for JSON API),
    which is automatically converted to snake_case"""

    class Thing(BaseNode):
        one_thing: int
        another_thing: str

    ModelManager.initialise_models(depth=3)

    thing = Thing(  # type: ignore
        **{
            "label": "something",
            "oneThing": 42,
            "anotherThing": "another thing",
        }
    )

    assert thing.one_thing == 42
    assert thing.another_thing == "another thing"


def test_abstract_declaration_not_inherited():
    class Thing(BaseNode):
        __abstract__ = True

    class Animal(Thing):
        pass

    class Pet(Animal):
        __abstract__ = True

    ModelManager.initialise_models(depth=3)

    assert Thing.__abstract__
    assert not Animal.__abstract__
    assert Pet.__abstract__


def test_non_heritable_mixins_are_inherited_directly():
    """Test NonHeritableMixins are inherited by direct child"""

    class Purchaseable(BaseNonHeritableMixin):
        price: int

    class Animal(BaseNode):
        name: str

    class Pet(Animal, Purchaseable):
        age: int

    ModelManager.initialise_models(depth=3)

    assert "name" in Pet.model_fields
    assert "age" in Pet.model_fields
    assert "price" in Pet.model_fields

    assert set(Pet._get_model_labels()) == set(
        ["BaseNode", "Purchaseable", "Animal", "Pet"]
    )


def test_non_heritable_mixins_are_not_inherited_indirectly():
    """Test NonHeritableMixins are not inherited by grandchild classes"""

    class Purchaseable(BaseNonHeritableMixin):
        price: int

    class Animal(BaseNode):
        name: str

    class Pet(Animal, Purchaseable):
        age: int

    class NonPurchaseablePet(Pet):
        something: int

    ModelManager.initialise_models(depth=3)

    assert "name" in Animal.model_fields
    assert "name" in Pet.model_fields
    assert "price" in Pet.model_fields

    # Check we have the expected inherited fields
    assert "name" in NonPurchaseablePet.model_fields
    assert "age" in NonPurchaseablePet.model_fields

    # But not the price, as we should not inherit from Purchaseable
    assert "price" not in NonPurchaseablePet.model_fields

    assert set(NonPurchaseablePet._get_model_labels()) == set(
        ["BaseNode", "NonPurchaseablePet", "Animal", "Pet"]
    )


def test_traits_keep_track_of_their_real_classes():
    class Purchaseable(BaseNonHeritableMixin):
        price: int

    class CheaplyPurchaseable(Purchaseable):
        pass

    class Punchable(BaseNonHeritableMixin):
        pass

    class Thing(BaseNode):
        pass

    class PurchaseableThing(Thing, Purchaseable):
        pass

    class Politician(BaseNode, Purchaseable, Punchable):
        pass

    class NonPurchaseablePolitician(Politician):
        pass

    class CheaplyPurchaseableThing(Thing, CheaplyPurchaseable):
        pass

    ModelManager.initialise_models(depth=3)

    assert Purchaseable.__pg_real_types_with_trait__ == set(
        [PurchaseableThing, Politician]
    )

    assert Punchable.__pg_real_types_with_trait__ == set([Politician])

    assert CheaplyPurchaseable.__pg_real_types_with_trait__ == set(
        [CheaplyPurchaseableThing]
    )


def test_embedded_cannot_be_in_model_name():
    with pytest.raises(PanglossConfigError):

        class EmbeddedSomething(BaseNode):
            pass


def test_embedded_does_not_need_to_be_wrapped_in_annotated():
    import datetime

    class DateBase(BaseNode):
        __abstract__ = True

    class DatePrecise(DateBase):
        date_precise: datetime.date

    class DateImprecise(DateBase):
        date_not_before: datetime.date
        date_not_after: datetime.date

    class Person(BaseNode):
        date_of_birth: Embedded[DateBase]

    ModelManager.initialise_models(depth=3)

    assert Person.embedded_nodes["date_of_birth"].embedded_class == DateBase


def test_embedded_model_tracks_base_class():
    class Thing(BaseNode):
        pass

    ModelManager.initialise_models()

    assert Thing.Embedded.base_class is Thing


def test_model_embedded_type_with_basic_fields():
    class Thing(BaseNode):
        age: int
        something_else: str

    ModelManager.initialise_models()

    assert Thing.Embedded
    assert "label" not in Thing.Embedded.model_fields
    assert set(Thing.Embedded.model_fields.keys()) == set(
        ["real_type", "uid", "age", "something_else"]
    )


def test_embedding_a_model():
    class Thing(BaseNode):
        pass

    class Parent(BaseNode):
        things_plain: Embedded[Thing]
        things_annotated: typing.Annotated[
            Embedded[Thing], EmbeddedConfig(validators=[annotated_types.MaxLen(3)])
        ]
        otherthings_plain: Embedded[OtherThing]
        otherthings_annotated: typing.Annotated[
            Embedded[OtherThing], EmbeddedConfig(validators=[annotated_types.MaxLen(1)])
        ]

        mixed_thing: Embedded[Thing | OtherThing]

    class OtherThing(BaseNode):
        pass

    ModelManager.initialise_models(depth=3)

    # Test annotations are returned with the correct types
    assert Parent.model_fields["things_plain"].annotation == list[Thing.Embedded]
    assert Parent.model_fields["things_annotated"].annotation == list[Thing.Embedded]
    assert (
        Parent.model_fields["otherthings_plain"].annotation == list[OtherThing.Embedded]
    )
    assert (
        Parent.model_fields["otherthings_annotated"].annotation
        == list[OtherThing.Embedded]
    )
    assert (
        Parent.model_fields["mixed_thing"].annotation
        == list[typing.Union[Thing.Embedded, OtherThing.Embedded]]
    )

    # Check default length (1) for non-specified annotation
    assert annotated_types.MinLen(1) in Parent.model_fields["things_plain"].metadata
    assert annotated_types.MaxLen(1) in Parent.model_fields["things_plain"].metadata

    # Assert defaults are not used when validators provided
    assert (
        annotated_types.MinLen(1)
        not in Parent.model_fields["things_annotated"].metadata
    )
    assert annotated_types.MaxLen(3) in Parent.model_fields["things_annotated"].metadata

    assert Parent.embedded_nodes["things_plain"].embedded_class == Thing


def test_double_model_embedding():
    class Inner(BaseNode):
        pass

    class Outer(BaseNode):
        has_inner: Embedded[Inner]

    class Parent(BaseNode):
        has_outer: Embedded[Outer]

    ModelManager.initialise_models(depth=3)

    assert Parent.model_fields["has_outer"].annotation == list[Outer.Embedded]
    assert Outer.model_fields["has_inner"].annotation == list[Inner.Embedded]
    assert Outer.Embedded.model_fields["has_inner"].annotation == list[Inner.Embedded]

    assert Parent.embedded_nodes["has_outer"].embedded_class == Outer
    assert Outer.embedded_nodes["has_inner"].embedded_class == Inner


def test_instantiating_double_embedded():
    class Inner(BaseNode):
        pass

    class Outer(BaseNode):
        has_inner: Embedded[Inner]

    class Parent(BaseNode):
        has_outer: Embedded[Outer]

    ModelManager.initialise_models(depth=3)

    p = Parent(
        label="A Parent",
        has_outer=[{"real_type": "outer", "has_inner": [{"real_type": "inner"}]}],
    )

    # Check things are instantiated with the right type
    assert isinstance(p.has_outer[0], Outer.Embedded)
    assert isinstance(p.has_outer[0].has_inner[0], Inner.Embedded)

    # Check we can also access embedded_nodes via proxy to main object
    assert p.has_outer[0].embedded_nodes == Outer.embedded_nodes
    assert p.has_outer[0].embedded_nodes["has_inner"].embedded_class == Inner


def test_model_relation_construction():
    class Person(BaseNode):
        pets: typing.Annotated[
            RelationTo[Pet],
            RelationConfig(
                reverse_name="is_owned_by", validators=[annotated_types.MaxLen(2)]
            ),
        ]

    class Pet(BaseNode):
        pass

    class Reptile(Pet):
        __abstract__ = True

    class Crocodile(Pet):
        pass

    ModelManager.initialise_models(depth=3)

    assert set(
        cl.__name__
        for cl in typing.get_args(
            typing.get_args(Person.model_fields["pets"].annotation)[0]
        )
    ) == {"PetReference", "CrocodileReference"}

    schema = Person.model_json_schema()

    assert {"$ref": "#/$defs/PetReference"} in schema["properties"]["pets"]["items"][
        "anyOf"
    ]
    assert {"$ref": "#/$defs/CrocodileReference"} in schema["properties"]["pets"][
        "items"
    ]["anyOf"]


def test_relation_to():
    class Pet(BaseNode):
        pass

    class Reptile(Pet):
        __abstract__ = True

    class Crocodile(Pet):
        pass

    class Person(BaseNode):
        pets: typing.Annotated[
            RelationTo[Pet],
            RelationConfig(
                reverse_name="is_owned_by", validators=[annotated_types.MaxLen(2)]
            ),
        ]

    ModelManager.initialise_models(depth=3)
    assert "pets" in Person.model_fields
    assert {
        arg.__name__
        for arg in Person.model_fields["pets"].annotation.__args__[0].__args__
    } == {"PetReference", "CrocodileReference"}

    # Test that that abstract Reptile is not included by
    # making sure that the length is only 2 (i.e. the above two)
    assert len(Person.model_fields["pets"].annotation.__args__[0].__args__) == 2  # type: ignore

    maxlen_validator, relation_config = Person.model_fields["pets"].metadata

    assert maxlen_validator == annotated_types.MaxLen(2)
    assert relation_config.reverse_name == "is_owned_by"
    assert relation_config.relation_to_base == Pet

    schema = Person.model_json_schema()

    assert {"$ref": "#/$defs/PetReference"} in schema["properties"]["pets"]["items"][
        "anyOf"
    ]
    assert {"$ref": "#/$defs/CrocodileReference"} in schema["properties"]["pets"][
        "items"
    ]["anyOf"]

    # Test that that abstract Reptile is not included by
    # making sure that the length is only 2 (i.e. the above two)
    assert len(schema["properties"]["pets"]["items"]["anyOf"]) == 2


def test_relation_to_with_union_type():
    class Person(BaseNode):
        pass

    class Cat(BaseNode):
        pass

    class Event(BaseNode):
        subject: typing.Annotated[
            RelationTo[Person | Cat], RelationConfig(reverse_name="is_subject_of")
        ]

    ModelManager.initialise_models(depth=3)


def test_reference_model_on_relation():
    class PersonPetRelation(RelationPropertiesModel):
        cost_of_purchase: int

    class Pet(BaseNode):
        name: str

        # class Reference:
        #    name: str
        #    weight: int

    class Crocodile(Pet):
        pass

    class Person(BaseNode):
        pets: typing.Annotated[
            RelationTo[Pet],
            RelationConfig(
                reverse_name="is_owned_by",
                validators=[annotated_types.MaxLen(2)],
                relation_model=PersonPetRelation,
            ),
        ]

    ModelManager.initialise_models(depth=3)

    p = Person(
        **{
            "label": "Tom Jones",
            "pets": [
                {
                    "name": "Mister Frisky",
                    "label": "Mr Frisky",
                    "real_type": "pet",
                    "relation_properties": {"cost_of_purchase": 200},
                },
                {
                    "name": "Mr Snappy",
                    "label": "Mr Snappy",
                    "real_type": "crocodile",
                    "relation_properties": {"cost_of_purchase": 300},
                },
            ],
        }
    )

    assert Person.model_fields["pets"].annotation
    assert typing.get_args(Person.model_fields["pets"].annotation)

    assert len(p.pets) == 2
    mf, ms = sorted(list(p.pets), key=lambda p: p.label)

    assert type(mf).__name__ == "Person__pets__PetReference"

    assert mf.label == "Mr Frisky"

    assert mf.relation_properties.cost_of_purchase == 200

    assert type(ms).__name__ == "Person__pets__CrocodileReference"
    assert ms.label == "Mr Snappy"
    assert ms.relation_properties.cost_of_purchase == 300


def test_relation_to_trait():
    class Purchaseable(BaseNonHeritableMixin):
        price: int

    class Thing(BaseNode):
        pass

    class PurchaseableThing(Thing, Purchaseable):
        pass

    class OtherPurchaseableThing(Thing, Purchaseable):
        pass

    class Pet(BaseNode):
        pass

    class Person(BaseNode):
        purchased_stuff: typing.Annotated[
            RelationTo[Purchaseable], RelationConfig(reverse_name="purchased_by")
        ]
        pets: typing.Annotated[
            RelationTo[Pet], RelationConfig(reverse_name="is_owned_by")
        ]

    class Organisation(BaseNode):
        purchased_stuff: typing.Annotated[
            RelationTo[Purchaseable], RelationConfig(reverse_name="purchased_by")
        ]

    ModelManager.initialise_models(depth=3)

    assert set(
        [
            m.__name__
            for m in Person.model_fields["purchased_stuff"]
            .annotation.__args__[0]
            .__args__
        ]
    ) == set(["OtherPurchaseableThingReference", "PurchaseableThingReference"])

    assert (
        Person.outgoing_relations["purchased_stuff"].target_base_class == Purchaseable
    )
    """TODO: add in once incoming rels are done
    assert len(PurchaseableThing.incoming_relations) == 1
    assert len(OtherPurchaseableThing.incoming_relations) == 1

    assert len(PurchaseableThing.incoming_relations["purchased_by"]) == 2
    assert {
        rel_def.origin_base_class
        for rel_def in PurchaseableThing.incoming_relations["purchased_by"]
    } == {Person, Organisation}

    assert len(OtherPurchaseableThing.incoming_relations["purchased_by"]) == 2
    assert {
        rel_def.origin_base_class
        for rel_def in OtherPurchaseableThing.incoming_relations["purchased_by"]
    } == {Person, Organisation}
    """


def test_reified_relation():
    # from pangloss_core.models_new import DataT

    class Person(BaseNode):
        has_thing: typing.Annotated[
            ThingIdentification[Thing],
            RelationConfig(reverse_name="is_thing_of_person"),
            ReifiedTargetConfig(reverse_name="is_target_of"),
        ]

    class Stuff(BaseNode):
        pass

    class Thing(BaseNode):
        pass  # something: int

    class ThingIdentification[T](ReifiedRelation[T]):
        identification_type: str
        has_stuff: typing.Annotated[
            RelationTo[Stuff], RelationConfig(reverse_name="person_identified_stuff")
        ]

    ModelManager.initialise_models(depth=3)

    assert Person.outgoing_relations["has_thing"].origin_base_class == Person
    assert set(
        Person.outgoing_relations["has_thing"].target_base_class.model_fields.keys()
    ) == set(["uid", "target", "identification_type", "has_stuff"])

    assert (
        typing.get_args(
            typing.get_args(
                Person.outgoing_relations["has_thing"]
                .target_base_class.model_fields["target"]
                .annotation
            )[0]
        )[0].__name__
        == "ThingReference"
    )

    p = Person(
        label="John Smith",
        has_thing=[
            {
                "identification_type": "nice",
                "has_stuff": [{"real_type": "stuff", "label": "some stuff"}],
                "target": [{"label": "A Thing"}],
            }
        ],
    )


def test_reified_relation_init_works():
    class IdentificationIdentifiedEntityRelation(RelationPropertiesModel):
        certainty: int

    class Identification[T](ReifiedRelation[T]):
        pass

    class Person(BaseNode):
        name: str

    class Event(BaseNode):
        person_identified: typing.Annotated[
            Identification[Person],
            RelationConfig(
                reverse_name="is_identification_of_person_in_event",
            ),
            ReifiedTargetConfig(
                reverse_name="is_identified_in",
                relation_model=IdentificationIdentifiedEntityRelation,
            ),
        ]

    ModelManager.initialise_models(depth=3)

    event = Event(
        label="Big Bash",
        person_identified=[
            {
                "target": [
                    dict(
                        label="JohnSmith",
                        real_type="person",
                        relation_properties=dict(certainty=1),
                    )
                ],
            }
        ],
    )

    person_identified = event.person_identified.pop()
    target = person_identified.target.pop()
    assert target.label == "JohnSmith"
    assert target.relation_properties.certainty == 1


def test_self_referencing_model():
    class Order(BaseNode):
        thing_ordered: typing.Annotated[
            RelationTo[Order | Payment], RelationConfig(reverse_name="was_ordered_in")
        ]

    class Payment(BaseNode):
        pass

    ModelManager.initialise_models(depth=3)

    assert "thing_ordered" in Order.model_fields
    assert {
        arg.__name__
        for arg in Order.model_fields["thing_ordered"].annotation.__args__[0].__args__
    } == {"OrderReference", "PaymentReference"}

    o = Order(
        label="the order",
        thing_ordered=[
            dict(
                real_type="order",
                label="order2",
                uid=uuid.uuid4(),
            ),
        ],
    )


def test_incoming_relation_definitions():
    class Pet(BaseNode):
        pass

    class Crocodile(Pet):
        pass

    class PersonPetRelation(RelationPropertiesModel):
        purchased_when: int

    class Person(BaseNode):
        pets: typing.Annotated[
            RelationTo[Pet],
            RelationConfig(
                reverse_name="is_owned_by", relation_model=PersonPetRelation
            ),
        ]

    class Dude(Person):
        pass

    class Organisation(BaseNode):
        pets: typing.Annotated[
            RelationTo[Pet], RelationConfig(reverse_name="is_owned_by")
        ]

    ModelManager.initialise_models(depth=3)

    assert len(Pet.incoming_relations) == 1

    pet_has_owner = Pet.incoming_relations["is_owned_by"]

    assert {p.origin_base_class for p in pet_has_owner} == {Dude, Organisation, Person}

    assert {p.origin_reference_class.__name__ for p in pet_has_owner} == {
        "OrganisationReference",
        "Pet__is_owned_by__PersonReference",
        "Pet__is_owned_by__DudeReference",
    }


# TODO: only View class needs reverse relations...OBVS?


def test_incoming_relations_through_embedded():
    """
    Incoming relations for a node should point to the outer node as well as the directly attached node.

    i.e. There is no distinction between Ref and Article (Ref is not *defined* as an embedded node itself),
    so Source.is_source_of should allow either Ref or Article as a type — Ref could always *not* be embedded...
    """

    class RefSourceProperty(RelationPropertiesModel):
        likelihood: int

    class Source(BaseNode):
        pass

    class Ref(BaseNode):
        page_number: int
        source: typing.Annotated[
            RelationTo[Source],
            RelationConfig(
                reverse_name="is_source_of", relation_model=RefSourceProperty
            ),
        ]

    class Article(BaseNode):
        reference: Embedded[Ref]

    ModelManager.initialise_models(depth=3)

    assert Source.incoming_relations["is_source_of"]

    assert len(Source.incoming_relations["is_source_of"]) == 2

    is_source_of_set = Source.incoming_relations["is_source_of"]

    assert {is_source_of.origin_base_class for is_source_of in is_source_of_set} == {
        Ref,
        Article,
    }


def test_incoming_relations_through_embedded_rel_to_trait():
    class Citable(BaseNonHeritableMixin):
        pass

    class WrittenSource(BaseNode, Citable):
        pass

    class ImageSource(BaseNode, Citable):
        pass

    class Ref(BaseNode):
        page_number: int
        source: typing.Annotated[
            RelationTo[Citable], RelationConfig(reverse_name="is_source_of")
        ]

    class Article(BaseNode):
        reference: Embedded[Ref]

    ModelManager.initialise_models(depth=3)

    assert WrittenSource.incoming_relations["is_source_of"]
    assert ImageSource.incoming_relations["is_source_of"]

    assert len(WrittenSource.incoming_relations["is_source_of"]) == 2
    assert len(ImageSource.incoming_relations["is_source_of"]) == 2

    assert {
        s.origin_base_class for s in WrittenSource.incoming_relations["is_source_of"]
    } == {Ref, Article}

    assert {
        s.origin_base_class for s in ImageSource.incoming_relations["is_source_of"]
    } == {Ref, Article}


def test_incoming_relations_through_double_embedded():
    class Dog(BaseNode):
        pass

    class Cat(BaseNode):
        pass

    class Tortoise(BaseNode):
        pass

    class DoubleInnerThing(BaseNode):
        tortoises: typing.Annotated[
            RelationTo[Tortoise], RelationConfig(reverse_name="tortoise_has_owner")
        ]

    class InnerThing(BaseNode):
        dogs: typing.Annotated[
            RelationTo[Dog], RelationConfig(reverse_name="dog_has_owner")
        ]
        double_inner_thing: Embedded[DoubleInnerThing]

    class Thing(BaseNode):
        inner_thing: Embedded[InnerThing]
        cats: typing.Annotated[
            RelationTo[Cat], RelationConfig(reverse_name="cat_has_owner")
        ]

    class Person(BaseNode):
        thing: Embedded[Thing]

    ModelManager.initialise_models(depth=3)

    assert Cat.incoming_relations["cat_has_owner"]

    # Cat should have 2 incoming relations: Person, Embedded
    assert len(Cat.incoming_relations["cat_has_owner"]) == 2
    assert {c.origin_base_class for c in Cat.incoming_relations["cat_has_owner"]} == {
        Person,
        Thing,
    }
    assert {c.target_base_class for c in Cat.incoming_relations["cat_has_owner"]} == {
        Cat
    }

    assert Dog.incoming_relations["dog_has_owner"]

    # Dog should have 3 incoming relation types: Person, Embedded, InnerEmbedded
    # assert len(Dog.incoming_relations["dog_has_owner"]) == 3

    assert {c.origin_base_class for c in Dog.incoming_relations["dog_has_owner"]} == {
        Person,
        Thing,
        InnerThing,
    }

    assert {
        c.origin_reference_class.__name__
        for c in Dog.incoming_relations["dog_has_owner"]
    } == {"PersonReference", "ThingReference", "InnerThingReference"}

    assert {c.target_base_class for c in Dog.incoming_relations["dog_has_owner"]} == {
        Dog
    }

    assert Tortoise.incoming_relations["tortoise_has_owner"]

    # Tortoise should have 4 incoming relation types: Person, Embedded, InnerEmbedded, DoubleInnerEmbedded
    assert len(Tortoise.incoming_relations["tortoise_has_owner"]) == 4

    assert {
        c.origin_base_class for c in Tortoise.incoming_relations["tortoise_has_owner"]
    } == {
        Person,
        Thing,
        InnerThing,
        DoubleInnerThing,
    }
