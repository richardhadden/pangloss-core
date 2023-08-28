from __future__ import annotations

import inspect
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    NewType,
    Optional,
    Self,
    Sequence,
    TypeVar,
    Union,
)
from uuid import UUID, uuid4

import humps
import pydantic
from annotated_types import BaseMetadata, MaxLen, MinLen
from icecream import ic
from pydantic.config import ConfigDict
from typing_extensions import Unpack

from pangloss_core.exceptions import PanglossConfigError


class CamelModel(pydantic.BaseModel):
    """Converts fields by default from Python snake_case to Javascript Schema CamelCase and back.

    Modified from Ahmed Nafies's code for Pydantic 2.0, which renames 'allow_population_by_name' to 'populate_by_name'
    """

    __author__ = "Ahmed Nafies <ahmed.nafies@gmail.com>"
    __copyright__ = "Copyright 2020, Ahmed Nafies"
    __license__ = "MIT"
    __version__ = "1.0.5"

    model_config = {"alias_generator": humps.camelize, "populate_by_name": True}


class ModelManagerClass(dict):
    """Stores references to all the defined Pangloss models.

    Model names are stored using kebab-case, which should be used for
    """

    def add_model(self, model_class: type[BaseNode]):
        self[humps.kebabize(model_class.__name__)] = model_class

    def __getitem__(self, __key: Any) -> Any:
        return super().__getitem__(humps.kebabize(__key))


ModelManager = ModelManagerClass()

RELATION_IDENTIFIER = "__relation__"
EMBEDDED_NODE_IDENTIFIER = "__embedded_node__"


class RelationModel(CamelModel):
    pass


class BaseNodeStandardFields(CamelModel):
    __abstract__ = True

    # Standard fields for all Reference types
    uid: UUID
    label: Annotated[str, MaxLen(500)]


class BaseNodeReference(BaseNodeStandardFields):
    # TODO: this is producing the option of relation model in JSON schema... It should only be null
    # Maybe should add this as a field on create_relation_model, so it's absent unless we have a relation model
    relation_properties: Optional[RelationModel | type[RelationModel]] = RelationModel()
    real_type: str = ""

    def __hash__(self):
        return hash(self.uid)


@dataclass
class _PG_OutgoingRelationDefinition:
    target_base_class: type[BaseNode]
    target_reference_class: type[BaseNodeReference]
    relation_config: _PG_RelationshipConfigInstantiated
    origin_base_class: type[BaseNode]


@dataclass
class _PG_IncomingRelationDefinition:
    origin_base_class: type[BaseNode]
    origin_reference_class: type[BaseNodeReference]
    relation_config: _PG_RelationshipConfigInstantiated
    target_base_class: type[BaseNode]

    def __hash__(self):
        return hash(
            repr(self.origin_base_class)
            + repr(self.origin_reference_class)
            + repr(self.relation_config)
        )


@dataclass
class _PG_EmbeddedNodeDefinition:
    embedded_class: type[BaseNode]
    embedded_config: _PG_EmbeddedConfigInstantiated


class BaseNode(BaseNodeStandardFields):
    """Base Node should be Abstract by default"""

    def __hash__(self):
        return hash(self.uid)

    __abstract__ = True

    Reference: ClassVar[type[BaseNodeReference]]
    outgoing_relations: ClassVar[dict[str, _PG_OutgoingRelationDefinition]]
    embedded_nodes: ClassVar[dict[str, _PG_EmbeddedNodeDefinition]]
    incoming_relations: ClassVar[dict[str, set[_PG_IncomingRelationDefinition]]]

    __inited_subclasses: ClassVar[set] = set()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        """
        Things to do here:

        1. Remove Trait classes: TICK
        2. Build labels: TICK
        3. Add class to ModelManager
        4. Build lists of Child Nodes, Relations, Reverse-Relations, RelatedReifications, ReverseRelatedReifications

        """
        # Check whether __abstract__ is a defined on the current class, not parent
        # and set the appropriate value on current class

        cls.__abstract__ = cls.__dict__.get("__abstract__", False)

        cls.__pg_run_init_subclass_checks__()

        # Call to delete properties from indirect trait fields
        cls.__pg_delete_indirect_trait_fields__()

        # Need to rebuild the model after deleting fields, to update everything properly

        cls.Reference = cls.__pg_create_reference_class__()
        cls.outgoing_relations = cls.__pg_get_relations_to__()
        cls.incoming_relations = {}
        cls.__pg_add_incoming_relations_to_related_models__()
        cls.embedded_nodes = cls.__pg_get_embedded_nodes__()
        cls.model_rebuild(force=True)

        ModelManager.add_model(cls)

    @classmethod
    def __pg_run_init_subclass_checks__(cls):
        for field_name, field in cls.model_fields.items():
            if field_name == "relation_properties":
                raise PanglossConfigError(
                    f"Field 'relation_properties' (on model {cls.__name__}) is a reserved name. Please rename this field."
                )

    @classmethod
    def __pg_add_incoming_relations_to_related_models__(cls):
        for relation_name, relation_definition in cls.__pg_get_relations_to__().items():
            if (
                relation_definition.relation_config.reverse_name
                in relation_definition.target_base_class.incoming_relations
            ):
                relation_definition.target_base_class.incoming_relations[
                    relation_definition.relation_config.reverse_name
                ].add(
                    _PG_IncomingRelationDefinition(
                        origin_base_class=cls,
                        origin_reference_class=cls.__pg_create_reference_class__(
                            relation_definition.relation_config.relation_model
                        ),
                        relation_config=relation_definition.relation_config,
                        target_base_class=relation_definition.target_base_class,
                    )
                )
            else:
                relation_definition.target_base_class.incoming_relations[
                    relation_definition.relation_config.reverse_name
                ] = set(
                    [
                        _PG_IncomingRelationDefinition(
                            origin_base_class=cls,
                            origin_reference_class=cls.__pg_create_reference_class__(
                                relation_definition.relation_config.relation_model
                            ),
                            relation_config=relation_definition.relation_config,
                            target_base_class=relation_definition.target_base_class,
                        )
                    ]
                )

    @classmethod
    def __pg_get_relations_to__(cls) -> dict[str, _PG_OutgoingRelationDefinition]:
        relations_to = {}
        for field_name, field in cls.model_fields.items():
            if RELATION_IDENTIFIER in field.metadata:
                # Get the relation_config (don't know its position in annotation necessarily)
                relation_config: _PG_RelationshipConfigInstantiated = [
                    item
                    for item in field.metadata
                    if isinstance(item, _PG_RelationshipConfigInstantiated)
                ][0]

                relations_to[field_name] = _PG_OutgoingRelationDefinition(
                    target_base_class=relation_config.relation_to_base,
                    target_reference_class=field.annotation.__args__[0],  # type: ignore
                    relation_config=relation_config,
                    origin_base_class=cls,
                )

        return relations_to

    @classmethod
    def __pg_get_embedded_nodes__(cls) -> dict[str, _PG_EmbeddedNodeDefinition]:
        embedded_nodes = {}
        for field_name, field in cls.model_fields.items():
            if EMBEDDED_NODE_IDENTIFIER in field.metadata:
                embedded_node_config: _PG_EmbeddedConfigInstantiated = [
                    item
                    for item in field.metadata
                    if isinstance(item, _PG_EmbeddedConfigInstantiated)
                ][0]

                embedded_nodes[field_name] = _PG_EmbeddedNodeDefinition(
                    embedded_class=embedded_node_config.embedded_node_base,
                    embedded_config=embedded_node_config,
                )
        return embedded_nodes

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
    def __pg_get_all_subclasses__(
        cls, include_abstract: bool = False
    ) -> set[type[BaseNode]]:
        subclasses = []
        for subclass in cls.__subclasses__():
            if not subclass.__abstract__ or include_abstract:
                subclasses += [subclass, *subclass.__pg_get_all_subclasses__()]
            else:
                subclasses += [*subclass.__pg_get_all_subclasses__()]
        return set(subclasses)

    def __init__(self, *args, **kwargs):
        # If "uid" is not provided, it is because it is new
        # and we need to create it to validate
        if not kwargs.get("uid", None):
            kwargs["uid"] = uuid4()

        super().__init__(*args, **kwargs)


@dataclass
class RelationConfig:
    """Provides configuration for a `RelationTo` type, e.g.:

    ```
    class Person:
        pets: RelationTo[Pet, RelationConfig(reverse_name="owned_by")]
    ```
    """

    reverse_name: str
    relation_model: Optional[type[RelationModel]] = None
    validators: Optional[Sequence[BaseMetadata]] = None


@dataclass
class _PG_RelationshipConfigInstantiated:
    """Internal version of RelationConfig for storing the config on
    relationship declaration. Avoids exposing the `relation_to_base` variable
    as something settable by user. Redeclares variables
    instead of inheriting from RelationConfig to avoid issue with ordering variables
    with default-less variables first, which is impossible when inheriting!"""

    reverse_name: str
    relation_to_base: type[BaseNode]
    relation_model: Optional[type[RelationModel]] = None
    validators: Optional[Sequence[BaseMetadata]] = None


@dataclass
class EmbeddedConfig:
    validators: Optional[Sequence[BaseMetadata]] = None


@dataclass
class _PG_EmbeddedConfigInstantiated:
    embedded_node_base: type[BaseNode]
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
        cls, args: tuple[type[RelationToType], RelationConfig]
    ) -> set[type[RelationToType]]:
        """Creates a Pydantic-friendly Annotated type"""

        try:
            related_type: type[BaseNode] = args[0]
        except TypeError:
            raise PanglossConfigError(
                "A RelationConfig instance must be provided as part of the type annotation"
            )

        related_type.model_rebuild(force=True)
        relation_config: RelationConfig = args[1]

        # Check if config validators are set, and if not, make an empty list for unpacking below
        validators = relation_config.validators if relation_config.validators else []

        # Build a new RelationConfigInstantiated model for the RelationConfig...
        # and add in the relation_to_base type
        relation_config = _PG_RelationshipConfigInstantiated(
            relation_to_base=related_type, **asdict(relation_config)  # type: ignore
        )
        # Get the subclasses of related-to cls, as possible allowed types
        # not including abstract classes
        related_types = tuple(
            [
                related_type.__pg_create_reference_class__(
                    relation_data_model=relation_config.relation_model
                ),
                *[
                    rt.__pg_create_reference_class__(
                        relation_data_model=relation_config.relation_model
                    )
                    for rt in related_type.__pg_get_all_subclasses__()
                ],
            ]
            if not related_type.__abstract__
            else tuple(
                [
                    rt.__pg_create_reference_class__(
                        relation_data_model=relation_config.relation_model
                    )
                    for rt in related_type.__pg_get_all_subclasses__()
                ]
            )
        )

        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*related_types]], *validators, relation_config, RELATION_IDENTIFIER]  # type: ignore


class EmbeddedNode(Sequence):
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
        cls, args: tuple[type[RelationToType], EmbeddedConfig]
    ) -> set[type[RelationToType]]:
        """Creates a Pydantic-friendly Annotated type"""

        try:
            embedded_node_type: type[BaseNode] = args[0]
        except TypeError:
            raise PanglossConfigError(
                "A RelationConfig instance must be provided as part of the type annotation"
            )

        embedded_node_type.model_rebuild(force=True)
        embedded_node_config: EmbeddedConfig = args[1]

        # Set the relation_config relation_to_base to the actual class concerned
        # Ignore type checking as we're cheating here...
        validators = (
            embedded_node_config.validators if embedded_node_config.validators else []
        )

        embedded_node_config_instantiated: _PG_EmbeddedConfigInstantiated = (
            _PG_EmbeddedConfigInstantiated(
                embedded_node_base=embedded_node_type, **asdict(embedded_node_config)
            )
        )

        # Get the subclasses of related-to cls, as possible allowed types
        embedded_node_types = (
            [embedded_node_type, *embedded_node_type.__pg_get_all_subclasses__()]
            if not embedded_node_type.__abstract__
            else embedded_node_type.__pg_get_all_subclasses__()
        )
        embedded_node_embedded_types = tuple(
            [
                pydantic.create_model(
                    f"{embedded_node_type.__name__}Embedded",
                    __base__=embedded_node_type,
                    real_type=(Literal[embedded_node_type.__name__.lower()], embedded_node_type.__name__.lower()),  # type: ignore
                )
                for embedded_node_type in embedded_node_types
            ]
        )

        # Check if config validators are set, and if not, make an empty list for unpacking below

        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*embedded_node_embedded_types]], *validators, embedded_node_config_instantiated, EMBEDDED_NODE_IDENTIFIER]  # type: ignore


class AbstractTrait:
    pass


class AbstractMixin(CamelModel):
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
