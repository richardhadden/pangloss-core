from uuid import uuid4

import pytest
from annotated_types import MaxLen

from pangloss_core.exceptions import PanglossConfigError
from pangloss_core.models import (
    RELATION_IDENTIFIER,
    AbstractTrait,
    BaseNode,
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


def test_basic_field_inheritance():
    """Test fields models are inherited with appropriate fields"""

    class Animal(BaseNode):
        name: str

    class Pet(Animal):
        pass

    assert "name" in Animal.model_fields
    assert "name" in Pet.model_fields


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

    class Crocodile(Pet):
        pass

    class Person(BaseNode):
        pets: RelationTo[
            Pet, RelationConfig(reverse_name="is_owned_by", validators=[MaxLen(2)])
        ]

    assert "pets" in Person.model_fields
    assert Person.model_fields["pets"].annotation.__args__[0].__args__[0].__name__ == "PetReference"  # type: ignore
    assert Person.model_fields["pets"].annotation.__args__[0].__args__[1].__name__ == "CrocodileReference"  # type: ignore

    maxlen_validator, relation_config, relation_identifier = Person.model_fields[
        "pets"
    ].metadata
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


"""
def test_build_reference_model():
    class Person(BaseNode):
        pass

    assert Person.Reference
    p = Person.Reference(uid=uuid4(), label="Tom Jones")
    assert p.real_type == "person"
"""


def test_reference_model_on_relation():
    class PersonPetRelation(RelationModel):
        cost_of_purchase: int

    class Pet(BaseNode):
        pass

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

    print(Person.model_json_schema())
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
                },
                {
                    "uid": uuid4(),
                    "label": "Mr Snappy",
                    "real_type": "crocodile",
                    "relation_data": {"cost_of_purchase": 200},
                },
            ],
        }
    )
    print(Person.model_json_schema())
    assert len(p.pets) == 2
