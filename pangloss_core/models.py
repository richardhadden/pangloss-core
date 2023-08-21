from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import lru_cache
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
)
from uuid import UUID

import pydantic
from annotated_types import BaseMetadata, MaxLen, MinLen
from icecream import ic
from pydantic.config import ConfigDict
from typing_extensions import Unpack

from pangloss_core.exceptions import PanglossConfigError


class ModelManager:
    pass


RELATION_IDENTIFIER = "__relation__"


class RelationModel(pydantic.BaseModel):
    pass


class BaseNodeStandardFields(pydantic.BaseModel):
    __abstract__ = True

    # Standard fields for all Reference types
    uid: UUID
    label: Annotated[str, MaxLen(500)]


class BaseNodeReference(BaseNodeStandardFields):
    relation_data: Optional[RelationModel | type[RelationModel]] = RelationModel()
    real_type: str = ""

    def __hash__(self):
        return hash(self.uid)


class BaseNode(BaseNodeStandardFields):
    """Base Node should be Abstract by default"""

    __abstract__ = True

    Reference: ClassVar[type[BaseNodeReference]]
    RelationsTo: ClassVar[dict[str, type[BaseNode]]]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        """
        Things to do here:

        1. Remove Trait classes: TICK
        2. Build labels: TICK
        3. Add class to ModelManager
        4. Build lists of Child Nodes, Relations, Reverse-Relations, RelatedReifications, ReverseRelatedReifications

        """

        cls.__pg_delete_indirect_trait_fields__()
        cls.model_rebuild(force=True)
        cls.Reference = cls.__pg_create_reference_class__()

    @classmethod
    def __pg_create_reference_class__(
        cls, relation_data_model: type[RelationModel] | None = None
    ) -> type[BaseNodeReference]:
        if not relation_data_model:
            return pydantic.create_model(
                f"{cls.__name__}Reference",
                __base__=BaseNodeReference,
                real_type=(Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
            )
        else:
            return pydantic.create_model(
                f"{relation_data_model.__name__}_{cls.__name__}Reference",
                __base__=BaseNodeReference,
                real_type=(Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
                relation_data=(relation_data_model, ...),
            )

    @classmethod
    @property
    @lru_cache
    def __pg_model_labels__(cls) -> list[str]:
        """All neo4j labels for model.

        Includes direct Trait names."""
        return [
            c.__name__
            for c in cls.mro()
            if (issubclass(c, BaseNode) and c is not BaseNode)
            or c in cls.__pg_traits_as_direct_ancestors__
        ]

    @classmethod
    def __pg_delete_indirect_trait_fields__(cls) -> None:
        trait_fields_to_delete = set()
        for trait in cls.__pg_traits_as_indirect_ancestors__:
            for field_name in cls.model_fields:
                # AND AND... not in the parent class annotations that is *not* a trait...
                if (
                    field_name in trait.__annotations__
                    and trait not in cls.__annotations__
                ):
                    trait_fields_to_delete.add(field_name)

        for field_to_delete in trait_fields_to_delete:
            del cls.model_fields[field_to_delete]

    @classmethod
    @property
    @lru_cache
    def __pg_traits_as_direct_ancestors__(cls) -> set[AbstractTrait]:
        """Identifies Traits that are directly applied to a model class"""
        traits_as_direct_bases = []
        for base in cls.__bases__:
            for parent in inspect.getmro(base):
                if parent is BaseNode:
                    break
                elif parent is AbstractTrait:
                    traits_as_direct_bases.append(base)
                else:
                    continue
        return set(traits_as_direct_bases)

    @classmethod
    @property
    @lru_cache
    def __pg_traits_as_indirect_ancestors__(cls) -> set[AbstractTrait]:
        traits_as_indirect_ancestors = []
        traits_as_direct_ancestors = cls.__pg_traits_as_direct_ancestors__
        for c in cls.mro():
            if (
                issubclass(c, AbstractTrait)
                and not issubclass(c, BaseNode)
                and c is not AbstractTrait
                and c is not cls
                and c not in traits_as_direct_ancestors
            ):
                traits_as_indirect_ancestors.append(c)
        return set(traits_as_indirect_ancestors)

    @classmethod
    @lru_cache
    def __pg_all_subclasses__(cls) -> set[type[BaseNode]]:
        subclasses = []
        for subclass in cls.__subclasses__():
            subclasses += [subclass, *subclass.__pg_all_subclasses__()]
        return set(subclasses)


@dataclass
class RelationConfig:
    reverse_name: str
    relation_to_base: ClassVar[Optional[type[BaseNode]]] = None
    relation_model: Optional[type[RelationModel]] = None
    validators: Optional[Sequence[BaseMetadata]] = None


RelationToType = TypeVar("RelationToType", type[BaseNode], type[BaseNode])


class RelationTo(Sequence):
    """Defines a RelationTo type annotation, e.g.:

    ```
    class Person(BaseNode):
        owns_pet: RelationTo[Pet, RelationConfig(reverse_name="is_owned_by")]
    ```
    The `RelationConfig` is required, and must at least provide a `reverse_name`.
    """

    # N.B. We inherit from Sequence so type checker allows us to call len() on this badboy
    # without complaining

    def __class_getitem__(
        cls, args: tuple[RelationToType, RelationConfig]
    ) -> set[type[RelationToType]]:
        """Creates a Pydantic-friendly Annotated type"""
        try:
            related_type: type[BaseNode] = args[0]
        except TypeError:
            raise PanglossConfigError(
                "A RelationConfig instance must be provided as part of the type annotation"
            )

        relation_config: RelationConfig = args[1]

        # Set the relation_config relation_to_base to the actual class concerned
        # Ignore type checking as we're cheating here...
        relation_config.relation_to_base = related_type  # type: ignore

        # Get the subclasses of related-to cls, as possible allowed types
        related_types = tuple(
            [
                related_type.__pg_create_reference_class__(
                    relation_data_model=relation_config.relation_model
                ),
                *[
                    rt.__pg_create_reference_class__(
                        relation_data_model=relation_config.relation_model
                    )
                    for rt in related_type.__pg_all_subclasses__()
                ],
            ]
        )

        # Check if config validators are set, and if not, make an empty list for unpacking below
        validators = relation_config.validators if relation_config.validators else []

        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*related_types]], *validators, relation_config, RELATION_IDENTIFIER]  # type: ignore


class AbstractTrait:
    pass


class AbstractMixin(pydantic.BaseModel):
    pass


"""
class Purchaseable(AbstractTrait):
    price: int

class ColourMixin(AbstractMixin):
    colour: str

class Vegetable(BaseNode, Purchaseable, ColourMixin):
    name: str
    weight: int


    
class NonPurchaseableVegetable(Vegetable, ColourMixin):
    pass

class AnotherNonPurchaseableVeg(NonPurchaseableVegetable):
    pass

class Person(BaseNode):
    owns_vegetable: RelationTo[Vegetable, RelationConfig(reverse_name="is_owned_by", validators=[MaxLen(1)])]

"""
"""
ic(Vegetable.model_fields)
ic(Vegetable.model_json_schema())
ic(NonPurchaseableVegetable.model_fields)
ic(NonPurchaseableVegetable.model_json_schema())

ic(Vegetable.__pros_model_labels__)
ic(NonPurchaseableVegetable.__pros_model_labels__)

npv = NonPurchaseableVegetable(uid="something", label="something", name="Swede", weight=100, colour="blue")
ic(npv.model_dump())
"""

# ic(Person.model_fields)
# ic(Person.model_json_schema())
