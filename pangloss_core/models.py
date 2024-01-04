from __future__ import annotations

import inspect
import typing
from collections import defaultdict
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import (
    Annotated,
    Any,
    Callable,
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

ClassPropertyType = TypeVar("ClassPropertyType")


class classproperty(Generic[ClassPropertyType]):
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """

    def __init__(self, method: Callable[[ClassPropertyType], Any]):
        self.fget = method

    def __get__(self, instance, cls: ClassPropertyType):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


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


def __pg_model_instantiates_abstract_trait__(
    cls: type[BaseNode] | type[AbstractMixin],
) -> bool:
    """Determines whether a Node model is a direct instantiation of a trait."""
    return issubclass(cls, AbstractTrait) and cls.__pg_is_subclass_of_trait__()


class RelationModel(CamelModel):
    """Parent class for relationship properties

    TODO: Check types on subclassing, to make sure only viable literals allowed"""

    pass


class BaseNodeStandardFields(CamelModel):
    """Class defining the standard fields for all Node models, Node reference models, etc."""

    __abstract__ = True

    # Standard fields for all Reference types
    uid: UUID
    label: Annotated[str, MaxLen(500)]


class BaseNodeReference(BaseNodeStandardFields):
    """Base class for all Node Reference models"""

    # TODO: this is producing the option of relation model in JSON schema... It should only be null
    # Maybe should add this as a field on create_relation_model, so it's absent unless we have a relation model
    relation_properties: Optional[RelationModel | type[RelationModel]] = RelationModel()
    real_type: str = ""

    def __hash__(self):
        return hash(self.uid)


@dataclass
class _PG_OutgoingRelationDefinition:
    """Class containing the definition of an outgoing node:

    - `target_base_class: type[BaseNode]`: the target ("to") class of the relationship
    - `target_reference_class: type[BaseNodeReference]`: the reference class of the target class
    - `relation_config: _PG_RelationshipConfigInstantiated`: the configuration model for the relationship
    - `origin_base_class: type[BaseNode]`: the origin ("from") class of the relationship
    """

    target_base_class: type[BaseNode]
    target_reference_class: type[BaseNodeReference]
    relation_config: _PG_RelationshipConfigInstantiated
    origin_base_class: type[BaseNode]

    def __hash__(self):
        return hash(
            repr(self.origin_base_class)
            + repr(self.target_base_class)
            + repr(self.relation_config)
        )


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
class _PG_IncomingRelationViaEmbeddedDefinition:
    origin_base_class: type[BaseNode]  # The origin of the reverse relation (the parent)
    origin_reference_class: type[BaseNodeReference]
    # embedded_base_class: type[BaseNode]
    origin_to_embedded_relation_config: _PG_EmbeddedConfigInstantiated

    # embedded_to_target_relation_config: _PG_RelationshipConfigInstantiated
    target_base_class: type[BaseNode]

    def __hash__(self):
        return hash(
            repr(self.origin_base_class)
            + repr(self.origin_reference_class)
            + repr(self.origin_to_embedded_relation_config)
            # + repr(self.embedded_base_class)
            # + repr(self.embedded_to_target_relation_config)
            + repr(self.target_base_class)
        )


@dataclass
class _PG_EmbeddedNodeDefinition:
    embedded_class: type[BaseNode]
    embedded_config: _PG_EmbeddedConfigInstantiated


class BaseNode(BaseNodeStandardFields):
    """Base Node should be Abstract by default"""

    __abstract__ = True

    def __hash__(self):
        return hash(self.uid)

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

        # Run all the checks for validity to model (to be added below as appropriate)
        cls.__pg_run_init_subclass_checks__()

        # Call to delete properties from indirect trait fields
        cls.__pg_delete_indirect_trait_fields__()

        # Need to rebuild the model after deleting fields, to update everything properly

        cls.Reference = cls.__pg_create_reference_class__()
        cls.embedded_nodes = cls.__pg_get_embedded_nodes__()

        cls.outgoing_relations = cls.__pg_get_relations_to__()

        cls.incoming_relations: dict[
            str, set[_PG_IncomingRelationDefinition]
        ] = defaultdict(set)
        cls.__pg_add_incoming_relations_to_related_models__()

        cls.incoming_relations_through_embedded: dict[
            str, set[_PG_IncomingRelationViaEmbeddedDefinition]
        ] = defaultdict(set)
        cls.__pg_add_incoming_relations_through_embedded__()

        cls.__pg_add_type_to_trait_list_of_real_types__()

        cls.model_rebuild(force=True)

        ModelManager.add_model(cls)

    @classmethod
    def __pg_add_type_to_trait_list_of_real_types__(cls):
        if issubclass(cls, AbstractTrait):
            for trait in cls.__pg_get_traits_as_direct_ancestors__():
                trait.__pg_real_types_with_trait__.add(cls)

    @classmethod
    def __pg_run_init_subclass_checks__(cls):
        """Run checks on subclasses for validity, following rules below.

        1. Cannot have field named `relation_properties` as this is used internally
        2. ..."""
        for field_name, field in cls.model_fields.items():
            if field_name == "relation_properties":
                raise PanglossConfigError(
                    f"Field 'relation_properties' (on model {cls.__name__}) is a reserved name. Please rename this field."
                )

    @staticmethod
    def __pg_recurse_embeddded_nodes_for_outgoing_types(
        this_class: type[BaseNode],
    ) -> set[_PG_OutgoingRelationDefinition]:
        """Starting from a particular model, work recursively through embedded nodes to find
        outgoing relationships."""
        relations = set()
        for (
            embedded_field_name,
            embedded_node_definition,
        ) in this_class.embedded_nodes.items():
            for (
                relation_name,
                relation_definition,
            ) in embedded_node_definition.embedded_class.outgoing_relations.items():
                relations.add(relation_definition)
                for (
                    rel
                ) in embedded_node_definition.embedded_class.__pg_recurse_embeddded_nodes_for_outgoing_types(
                    embedded_node_definition.embedded_class
                ):
                    if not getattr(rel.origin_base_class, "is_embedded_type", False):
                        relations.add(rel)

        return relations

    @classmethod
    def __pg_add_incoming_relations_through_embedded__(cls):
        # Don't add reverse relations to embedded types! Just the real types...
        if getattr(cls, "is_embedded_type", False):
            return

        for (
            embedded_field_name,
            embedded_node_definition,
        ) in cls.embedded_nodes.items():
            # print(embedded_field_name, embedded_node_definition)

            if __pg_model_instantiates_abstract_trait__(
                embedded_node_definition.embedded_class
            ):
                """TODO: Here, we need to add this for all types of embedded trait...

                Extract the thing below as function, and iterate over it...
                """
                continue

            # For each embedded class's outgoing relations, add the relation to incoming
            # of the target of the relation
            for (
                relation_name,
                relation_definition,
            ) in embedded_node_definition.embedded_class.outgoing_relations.items():
                # If the target is a trait, add the real versions...
                if __pg_model_instantiates_abstract_trait__(
                    relation_definition.target_base_class
                ) and issubclass(relation_definition.target_base_class, AbstractTrait):
                    for (
                        target_base_class
                    ) in (
                        relation_definition.target_base_class.__pg_real_types_with_trait__
                    ):
                        rel_def = _PG_IncomingRelationDefinition(
                            origin_base_class=cls,
                            origin_reference_class=cls.Reference,
                            relation_config=relation_definition.relation_config,
                            target_base_class=target_base_class,
                        )
                        target_base_class.incoming_relations[
                            relation_definition.relation_config.reverse_name
                        ].add(rel_def)
                # Otherwise, just add the class...
                else:
                    rel_def = _PG_IncomingRelationDefinition(
                        origin_base_class=cls,
                        origin_reference_class=cls.Reference,
                        relation_config=relation_definition.relation_config,
                        target_base_class=relation_definition.target_base_class,
                    )

                    relation_definition.target_base_class.incoming_relations[
                        relation_definition.relation_config.reverse_name
                    ].add(rel_def)

                # Now go through all the embedded classes recursively and add these as well
                incoming_relation_definitions = (
                    cls.__pg_recurse_embeddded_nodes_for_outgoing_types(cls)
                )

                for incoming_relation_definition in incoming_relation_definitions:
                    # If it's a trait, add the real classes
                    if __pg_model_instantiates_abstract_trait__(
                        incoming_relation_definition.target_base_class
                    ) and issubclass(
                        incoming_relation_definition.target_base_class, AbstractTrait
                    ):
                        for (
                            target_base_class
                        ) in (
                            incoming_relation_definition.target_base_class.__pg_real_types_with_trait__
                        ):
                            rel_def = _PG_IncomingRelationDefinition(
                                origin_base_class=cls,
                                origin_reference_class=cls.Reference,
                                relation_config=incoming_relation_definition.relation_config,
                                target_base_class=target_base_class,
                            )
                            target_base_class.incoming_relations[
                                incoming_relation_definition.relation_config.reverse_name
                            ].add(rel_def)

                    # Otherwise, add the actual class
                    else:
                        rel_def = _PG_IncomingRelationDefinition(
                            origin_base_class=cls,
                            origin_reference_class=cls.Reference,
                            relation_config=incoming_relation_definition.relation_config,
                            target_base_class=incoming_relation_definition.target_base_class,
                        )

                        incoming_relation_definition.target_base_class.incoming_relations[
                            incoming_relation_definition.relation_config.reverse_name
                        ].add(
                            rel_def
                        )

    @classmethod
    def __pg_add_incoming_relations_to_related_models__(cls):
        # Don't add embedded node defs as reverse relations
        if getattr(cls, "is_embedded_type", False):
            return

        for relation_name, relation_definition in cls.__pg_get_relations_to__().items():
            # If reverse relation is to a trait, then we need all the possible instantiating-types
            # of that trait

            if (
                issubclass(relation_definition.target_base_class, AbstractTrait)
                and relation_definition.target_base_class.__pg_is_subclass_of_trait__()
            ):
                for (
                    target_base_class
                ) in relation_definition.target_base_class.__pg_real_types_with_trait__:
                    # If there is no

                    target_base_class.incoming_relations[
                        relation_definition.relation_config.reverse_name
                    ].add(
                        _PG_IncomingRelationDefinition(
                            origin_base_class=cls,
                            origin_reference_class=cls.__pg_create_reference_class__(
                                relation_definition.relation_config.relation_model
                            ),
                            relation_config=relation_definition.relation_config,
                            target_base_class=target_base_class,
                        )
                    )

            else:
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

                # TODO: think about this... do we want single classes, or all the subtypes as well?

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
    def __pg_get_model_labels__(cls) -> list[str]:
        """All neo4j labels for model.

        Includes direct Trait names."""
        return [
            c.__name__
            for c in cls.mro()
            if (issubclass(c, BaseNode) and c is not BaseNode)
            or c in cls.__pg_get_traits_as_direct_ancestors__()
        ]

    @classmethod
    def __pg_delete_indirect_trait_fields__(cls) -> None:
        trait_fields_to_delete = set()
        for trait in cls.__pg_get_traits_as_indirect_ancestors__():
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
    def __pg_get_traits_as_direct_ancestors__(cls) -> set[AbstractTrait]:
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
    def __pg_get_traits_as_indirect_ancestors__(cls) -> set[AbstractTrait]:
        traits_as_indirect_ancestors = []
        traits_as_direct_ancestors = cls.__pg_get_traits_as_direct_ancestors__()
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

    @classmethod
    def __pg_create_annotation_for_relation_to_concrete_class__(
        cls, related_type: type[RelationToType], relation_config: RelationConfig
    ) -> set[type[RelationToType]]:
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

    @classmethod
    def __pg_create_annotation_for_relation_to_trait__(
        cls, related_type: type[AbstractTrait], relation_config: RelationConfig
    ) -> set[type[BaseNode]]:
        validators = relation_config.validators if relation_config.validators else []

        concrete_related_types: set[
            type[BaseNode]
        ] = related_type.__pg_real_types_with_trait__

        relation_config = _PG_RelationshipConfigInstantiated(
            relation_to_base=related_type, **asdict(relation_config)  # type: ignore
        )

        all_related_types = []
        for concrete_related_type in concrete_related_types:
            # ic(concrete_related_type)
            # ic(relation_config)
            # Build a new RelationConfigInstantiated model for the RelationConfig...
            # and add in the relation_to_base type

            # Get the subclasses of related-to cls, as possible allowed types
            # not including abstract classes
            all_related_types.append(
                concrete_related_type.__pg_create_reference_class__(
                    relation_data_model=relation_config.relation_model
                )
            )
        all_related_types = tuple(all_related_types)
        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*all_related_types]], *validators, relation_config, RELATION_IDENTIFIER]  # type: ignore

    def __class_getitem__(
        cls, args: tuple[type[RelationToType] | type[AbstractTrait], RelationConfig]
    ) -> set[type[RelationToType] | type[BaseNode]]:
        """Creates a Pydantic-friendly Annotated type"""

        try:
            related_type: type[BaseNode] | type[AbstractTrait] = args[0]
        except TypeError:
            raise PanglossConfigError(
                "A RelationConfig instance must be provided as part of the type annotation"
            )
        relation_config: RelationConfig = args[1]

        if (
            issubclass(related_type, AbstractTrait)
            and related_type.__pg_is_subclass_of_trait__()
        ):
            return cls.__pg_create_annotation_for_relation_to_trait__(
                related_type=related_type, relation_config=relation_config
            )

        else:
            related_type = typing.cast(type[BaseNode], related_type)
            return cls.__pg_create_annotation_for_relation_to_concrete_class__(
                related_type=related_type, relation_config=relation_config
            )


class EmbeddedNode(Sequence):
    """Defines an Embedded Node type annotation, e.g.:

    ```
    class Person(BaseNode):
        date_of_birth: EmbeddedNode[Date, EmbeddedConfig(validators=[MaxLen(1)])]
    ```
    The `EmbeddedConfig` is optional (by default, cardinality of an embedded node is 1)
    """

    # N.B. We inherit from Sequence so type checker allows us to call len() on this badboy
    # without complaining

    # TODO: can also embed traits, MFs!

    @classmethod
    def __pg_create_annotation_for_embedded_node__(
        cls,
        embedded_node_type: type[RelationToType],
        embedded_node_config: EmbeddedConfig,
    ) -> set[type[RelationToType]]:
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
                    is_embedded_type=(ClassVar[bool], True),
                )
                for embedded_node_type in embedded_node_types
            ]
        )

        # Check if config validators are set, and if not, make an empty list for unpacking below

        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*embedded_node_embedded_types]], *validators, embedded_node_config_instantiated, EMBEDDED_NODE_IDENTIFIER]  # type: ignore

    @classmethod
    def __pg_create_annotation_for_embedded_trait__(
        cls,
        embedded_node_type: type[AbstractTrait],
        embedded_node_config: RelationConfig,
    ) -> set[type[BaseNode]]:
        validators = (
            embedded_node_config.validators if embedded_node_config.validators else []
        )

        concrete_embedded_types: set[
            type[BaseNode]
        ] = embedded_node_type.__pg_real_types_with_trait__

        embedded_node_config = _PG_EmbeddedConfigInstantiated(
            embedded_node_base=embedded_node_type, **asdict(embedded_node_config)  # type: ignore
        )

        embedded_node_embedded_types = []

        # ic(concrete_related_type)
        # ic(relation_config)
        # Build a new RelationConfigInstantiated model for the RelationConfig...
        # and add in the relation_to_base type

        # Get the subclasses of related-to cls, as possible allowed types
        # not including abstract classes
        embedded_node_embedded_types = []
        for concrete_embedded_type in concrete_embedded_types:
            ic(concrete_embedded_type)
            embedded_node_embedded_types.append(
                pydantic.create_model(
                    f"{concrete_embedded_type.__name__}Embedded",
                    __base__=concrete_embedded_type,
                    real_type=(Literal[concrete_embedded_type.__name__.lower()], concrete_embedded_type.__name__.lower()),  # type: ignore
                    is_embedded_type=(ClassVar[bool], True),
                )
            )

        embedded_node_embedded_types = tuple(embedded_node_embedded_types)
        # Return a Pydantic-friendly Annotated[] type
        # Need to do this # type: ignore hack here, as we are basically lying to the type checker
        # about what we are returning (dynamically constructing a list of sub-types)
        return Annotated[set[Union[*embedded_node_embedded_types]], *validators, embedded_node_config, EMBEDDED_NODE_IDENTIFIER]  # type: ignore

    def __class_getitem__(
        cls, args: type[RelationToType] | tuple[type[RelationToType], EmbeddedConfig]
    ) -> set[type[RelationToType]]:
        """Creates a Pydantic-friendly Annotated type"""

        if isinstance(args, tuple) and len(args) == 2:
            if not inspect.isclass(args[0]) or not issubclass(
                args[0], (BaseNode, AbstractTrait)
            ):
                raise PanglossConfigError(
                    f"The first argument to EmbeddedNode must be a subclass of BaseNode, not {type(args[0]).__name__}"
                )

            if not isinstance(args[1], EmbeddedConfig):
                raise PanglossConfigError(
                    f"The second (optional) argument to EmbeddedNode must be an instance of EmbeddedConfig, not {type(args).__name__}"
                )

            embedded_node_type: type[BaseNode] | type[AbstractTrait] = args[0]
            embedded_node_config: EmbeddedConfig = args[1]
        else:
            if not inspect.isclass(args) or not issubclass(
                args, (BaseNode, AbstractTrait)
            ):
                raise PanglossConfigError(
                    f"The first argument to EmbeddedNode must be a subclass of BaseNode, not {type(args).__name__}"
                )

            embedded_node_type: type[BaseNode] | type[AbstractTrait] = args
            embedded_node_config: EmbeddedConfig = EmbeddedConfig()

        if (
            issubclass(embedded_node_type, AbstractTrait)
            and embedded_node_type.__pg_is_subclass_of_trait__()
        ):
            return cls.__pg_create_annotation_for_embedded_trait__(
                embedded_node_type=embedded_node_type,
                embedded_node_config=embedded_node_config,
            )

        elif issubclass(embedded_node_type, BaseNode):
            return cls.__pg_create_annotation_for_embedded_node__(
                embedded_node_type=embedded_node_type,
                embedded_node_config=embedded_node_config,
            )

        else:
            raise PanglossConfigError("Something went wrong")

        # embedded_node_type.model_rebuild(force=True)

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
    __pg_real_types_with_trait__: set[type[BaseNode]]

    @classmethod
    def __pg_is_subclass_of_trait__(cls):
        """Determine whether a class is a subclass of AbstractTrait,
        not the application of a trait to a real BaseNode class.

        This should work by not having BaseNode in its class hierarchy
        """
        for parent in cls.mro()[1:]:
            if issubclass(parent, BaseNode):
                return False
        else:
            return True

    def __init_subclass__(cls):
        cls.__pg_real_types_with_trait__ = set()


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
