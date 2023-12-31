from __future__ import annotations

import datetime
from uuid import uuid4

import pytest
from annotated_types import MaxLen

from pangloss_core.exceptions import PanglossConfigError
from pangloss_core.models import (
    RELATION_IDENTIFIER,
    AbstractTrait,
    BaseNode,
    BaseNodeReference,
    EmbeddedConfig,
    EmbeddedNode,
    ModelManager,
    RelationConfig,
    RelationModel,
    RelationTo,
)


def test_model_init():
    """Test initialisation of a BaseNode.

    Basic sanity check to make sure any other modifications of BaseNode don't prevent initialisation
    """

    class Thing(BaseNode):
        name: str
        age: int

    thing = Thing(uid=uuid4(), label="Someone", name="Someone", age=42)

    assert thing.label == "Someone"


def test_model_init_from_camel_dict():
    """Tests that models can be populated by the equivalent camelCase (standard for JSON API),
    which is automatically converted to snake_case"""

    class Thing(BaseNode):
        one_thing: int
        another_thing: str

    thing = Thing(  # type: ignore
        **{
            "uid": uuid4(),
            "label": "something",
            "oneThing": 42,
            "anotherThing": "another thing",
        }
    )

    assert thing.one_thing == 42


def test_relation_properties_not_allowed_as_field_name():
    with pytest.raises(PanglossConfigError):

        class Thing(BaseNode):
            relation_properties: int


def test_basic_field_inheritance():
    """Test fields models are inherited with appropriate fields"""

    class Animal(BaseNode):
        name: str

    class Pet(Animal):
        pass

    assert "name" in Animal.model_fields
    assert "name" in Pet.model_fields


def test_abstract_declaration_not_inherited():
    class Thing(BaseNode):
        __abstract__ = True

    class Animal(Thing):
        pass

    class Pet(Animal):
        __abstract__ = True

    assert Thing.__abstract__
    assert not Animal.__abstract__
    assert Pet.__abstract__


def test_basenode_subclasses():
    class Thing(BaseNode):
        __abstract__ = True

    class Animal(Thing):
        __abstract__ = True

    class Pet(Animal):
        pass

    class Dog(Animal):
        pass

    assert Thing.__pg_get_all_subclasses__() == {Pet, Dog}
    assert Thing.__pg_get_all_subclasses__(include_abstract=True) == {Animal, Pet, Dog}


def test_model_labels():
    """Test labels are inherited"""

    class Animal(BaseNode):
        name: str

    class Pet(Animal):
        pass

    assert Animal.__pg_model_labels__ == ["Animal"]
    assert set(Pet.__pg_model_labels__) == set(["Pet", "Animal"])


def test_traits_are_inherited_directly():
    """Test Traits are inherited by direct child"""

    class Purchaseable(AbstractTrait):
        price: int

    class Animal(BaseNode):
        name: str

    class Pet(Animal, Purchaseable):
        age: int

    assert "name" in Pet.model_fields
    assert "age" in Pet.model_fields
    assert "price" in Pet.model_fields

    assert set(Pet.__pg_model_labels__) == set(["Purchaseable", "Animal", "Pet"])


def test_traits_are_not_inherited_indirectly():
    """Test Traits are not inherited by grandchild classes"""

    class Purchaseable(AbstractTrait):
        price: int

    class Animal(BaseNode):
        name: str

    class Pet(Animal, Purchaseable):
        age: int

    class NonPurchaseablePet(Pet):
        pass

    # Check we have the expected inherited fields
    assert "name" in NonPurchaseablePet.model_fields
    assert "age" in NonPurchaseablePet.model_fields

    # But not the price, as we should not inherit from Purchaseable
    assert "price" not in NonPurchaseablePet.model_fields

    assert set(NonPurchaseablePet.__pg_model_labels__) == set(
        ["NonPurchaseablePet", "Animal", "Pet"]
    )


def test_relation_to_fails_without_relationconfig():
    """Test using a RelationTo without a RelationConfig object throws an ConfigError"""
    with pytest.raises(PanglossConfigError):

        class Pet(BaseNode):
            pass

        class Person(BaseNode):
            pets: RelationTo[Pet]


def test_relation_to():
    class Pet(BaseNode):
        pass

    class Reptile(Pet):
        __abstract__ = True

    class Crocodile(Pet):
        pass

    class Person(BaseNode):
        pets: RelationTo[
            Pet, RelationConfig(reverse_name="is_owned_by", validators=[MaxLen(2)])
        ]

    assert "pets" in Person.model_fields
    assert Person.model_fields["pets"].annotation.__args__[0].__args__[0].__name__ == "PetReference"  # type: ignore
    assert Person.model_fields["pets"].annotation.__args__[0].__args__[1].__name__ == "CrocodileReference"  # type: ignore

    # Test that that abstract Reptile is not included by
    # making sure that the length is only 2 (i.e. the above two)
    assert len(Person.model_fields["pets"].annotation.__args__[0].__args__) == 2  # type: ignore

    maxlen_validator, relation_config, relation_identifier = Person.model_fields[
        "pets"
    ].metadata
    print("petfieldmetadata", Person.model_fields["pets"])
    assert maxlen_validator == MaxLen(2)
    assert relation_config.reverse_name == "is_owned_by"
    assert relation_config.relation_to_base == Pet
    assert relation_identifier == RELATION_IDENTIFIER

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


def test_build_reference_model():
    class Person(BaseNode):
        pass

    assert Person.Reference
    p = Person.Reference(uid=uuid4(), label="Tom Jones")
    assert p.real_type == "person"


def test_reference_model_on_relation():
    class PersonPetRelation(RelationModel):
        cost_of_purchase: int

    class Pet(BaseNode):
        name: str

        class Reference:
            name: str
            weight: int

    class Crocodile(Pet):
        pass

    class Person(BaseNode):
        pets: RelationTo[
            Pet,
            RelationConfig(
                reverse_name="is_owned_by",
                validators=[MaxLen(2)],
                relation_model=PersonPetRelation,
            ),
        ]

    p = Person(
        **{
            "uid": uuid4(),
            "label": "Tom Jones",
            "pets": [
                {
                    "uid": uuid4(),
                    "label": "Mr Frisky",
                    "real_type": "pet",
                    "relation_data": {"cost_of_purchase": 200},
                    "weight": 100,
                },
                {
                    "uid": uuid4(),
                    "label": "Mr Snappy",
                    "real_type": "crocodile",
                    "relation_data": {"cost_of_purchase": 300},
                },
            ],
        }
    )
    assert len(p.pets) == 2
    mf, ms = sorted(list(p.pets), key=lambda p: p.label)

    assert type(mf).__name__ == "PersonPetRelation_PetReference"

    assert mf.label == "Mr Frisky"

    assert mf.relation_data.cost_of_purchase == 200

    assert type(ms).__name__ == "PersonPetRelation_CrocodileReference"
    assert ms.label == "Mr Snappy"
    assert ms.relation_data.cost_of_purchase == 300


def test_embedded_node():
    class DateBase(BaseNode):
        __abstract__ = True

    class DatePrecise(DateBase):
        date_precise: datetime.date

    class DateImprecise(DateBase):
        date_not_before: datetime.date
        date_not_after: datetime.date

    class Person(BaseNode):
        date_of_birth: EmbeddedNode[DateBase, EmbeddedConfig(validators=[MaxLen(1)])]

    assert "DatePreciseEmbedded" in [
        c.__name__
        for c in Person.model_fields["date_of_birth"].annotation.__args__[0].__args__  # type: ignore
    ]
    assert "DateImpreciseEmbedded" in [
        c.__name__
        for c in Person.model_fields["date_of_birth"].annotation.__args__[0].__args__  # type: ignore
    ]
    assert "DateBaseEmbedded" not in [
        c.__name__
        for c in Person.model_fields["date_of_birth"].annotation.__args__[0].__args__  # type: ignore
    ]

    p = Person(
        **{
            "uid": uuid4(),
            "label": "Tom Jones",
            "date_of_birth": [
                {
                    "label": "some date label",
                    "date_not_before": datetime.date.today(),
                    "date_not_after": datetime.date.today(),
                    "real_type": "dateimprecise",
                }
            ],
        }
    )

    assert list(p.date_of_birth)[0].real_type == "dateimprecise"
    assert list(p.date_of_birth)[0].date_not_before == datetime.date.today()


def test_get_relations_to():
    class Pet(BaseNode):
        pass

    class Person(BaseNode):
        pets: RelationTo[Pet, RelationConfig(reverse_name="has_owner")]

    assert (
        Person.__pg_get_relations_to__()["pets"].target_reference_class.__name__
        == "PetReference"
    )
    assert Person.__pg_get_relations_to__()["pets"].target_base_class == Pet
    assert (
        Person.outgoing_relations["pets"].target_reference_class.__name__
        == "PetReference"
    )


def test_get_embedded_nodes():
    class Date(BaseNode):
        date: datetime.date

    class Person(BaseNode):
        date_of_birth: EmbeddedNode[Date, EmbeddedConfig()]

    assert Person.__pg_get_embedded_nodes__()["date_of_birth"].embedded_class == Date
    assert (
        Person.__pg_get_embedded_nodes__()[
            "date_of_birth"
        ].embedded_config.embedded_node_base
        == Date
    )

    assert Person.embedded_nodes["date_of_birth"].embedded_class == Date


def test_embedded_node_does_not_need_config():
    class Date(BaseNode):
        date: datetime.date

    class Person(BaseNode):
        date_of_birth: EmbeddedNode[Date]


def test_embedded_node_checks():
    with pytest.raises(PanglossConfigError):

        class Person(BaseNode):
            date_of_birth: EmbeddedNode["balls"]


def test_incoming_relations():
    """Incoming relation definitions should allow same reverse_name to be used on
    multiple classes, and should create a unique definition for each"""

    # Now the classes of the test
    class Pet(BaseNode):
        pass

    class Crocodile(Pet):
        pass

    class PersonPetRelation(RelationModel):
        purchased_when: datetime.date

    class Person(BaseNode):
        nuns: RelationTo[
            Pet,
            RelationConfig(
                reverse_name="is_owned_by", relation_model=PersonPetRelation
            ),
        ]

    class Dude(Person):
        pass

    class Organisation(BaseNode):
        nuns: RelationTo[Pet, RelationConfig(reverse_name="is_owned_by")]

    assert len(Pet.incoming_relations) == 1

    nun_has_owner = Pet.incoming_relations["is_owned_by"]

    assert len(nun_has_owner) == 3

    types_to_be_connected_to = set([Person, Dude, Organisation])

    incoming_related_types = set([ir.origin_base_class for ir in nun_has_owner])

    assert types_to_be_connected_to.issubset(incoming_related_types)


def test_add_to_model_manager():
    class Person(BaseNode):
        pass

    class OneThing(BaseNode):
        pass

    assert ModelManager["person"]
    assert ModelManager["Person"]

    assert ModelManager["one_thing"]
    assert ModelManager["OneThing"]
    assert ModelManager["one-thing"]


def test_traits_keep_track_of_their_real_classes():
    class Purchaseable(AbstractTrait):
        price: int

    class CheaplyPurchaseable(Purchaseable):
        pass

    class Punchable(AbstractTrait):
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

    assert Purchaseable.__pg_real_types_with_trait__ == set(
        [PurchaseableThing, Politician]
    )

    assert Punchable.__pg_real_types_with_trait__ == set([Politician])

    assert CheaplyPurchaseable.__pg_real_types_with_trait__ == set(
        [CheaplyPurchaseableThing]
    )


def test_subclass_of_trait():
    class Purchaseable(AbstractTrait):
        price: int

    class Thing(BaseNode):
        pass

    class PurchaseableThing(Thing, Purchaseable):
        pass

    assert Purchaseable.__pg_is_subclass_of_trait__
    assert not PurchaseableThing.__pg_is_subclass_of_trait__


def test_relation_to_trait():
    class Purchaseable(AbstractTrait):
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
        purchased_stuff: RelationTo[
            Purchaseable, RelationConfig(reverse_name="purchased_by")
        ]
        pets: RelationTo[Pet, RelationConfig(reverse_name="is_owned_by")]

    class Organisation(BaseNode):
        purchased_stuff: RelationTo[
            Purchaseable, RelationConfig(reverse_name="purchased_by")
        ]

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


def test_embedded_trait():
    class Purchaseable(AbstractTrait):
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
        purchased_stuff: EmbeddedNode[Purchaseable]

    assert Person.embedded_nodes["purchased_stuff"]


# TODO: Embedded traits
# TODO: relations to traits DONE!
# TODO: abstract reifications
