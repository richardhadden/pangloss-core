import dataclasses
import types
import typing

import annotated_types

from pangloss_core_new.model_setup.models_base import CamelModel

if typing.TYPE_CHECKING:
    from pangloss_core_new.model_setup.base_node_definitions import (
        AbstractBaseNode,
        BaseMixin,
        BaseNonHeritableMixin,
    )
    from pangloss_core_new.model_setup.reference_node_base import BaseNodeReference


class RelationPropertiesModel(CamelModel):
    """Parent class for relationship properties

    TODO: Check types on subclassing, to make sure only viable literals allowed"""

    pass


@dataclasses.dataclass
class RelationConfig:
    """Provides configuration for a `RelationTo` type, e.g.:

    ```
    class Person:
        pets: RelationTo[Pet, RelationConfig(reverse_name="owned_by")]
    ```
    """

    reverse_name: str
    relation_model: typing.Optional[type[RelationPropertiesModel]] = None
    validators: typing.Optional[typing.Sequence[annotated_types.BaseMetadata]] = None
    subclasses_relation: typing.Optional[str] = None
    create_inline: bool = False
    edit_inline: bool = False
    delete_related_on_detach: bool = False


@dataclasses.dataclass
class _PG_RelationshipConfigInstantiated:
    """Internal version of RelationConfig for storing the config on
    relationship declaration. Avoids exposing the `relation_to_base` variable
    as something settable by user. Redeclares variables
    instead of inheriting from RelationConfig to avoid issue with ordering variables
    with default-less variables first, which is impossible when inheriting!"""

    reverse_name: str
    relation_to_base: type["AbstractBaseNode"]
    relation_model: typing.Optional[type[RelationPropertiesModel]] = None
    validators: typing.Optional[typing.Sequence[annotated_types.BaseMetadata]] = None
    subclasses_relation: typing.Optional[str] = None
    relation_labels: set[str] = dataclasses.field(default_factory=set)
    create_inline: bool = False
    edit_inline: bool = False
    delete_related_on_detach: bool = False


@dataclasses.dataclass
class _PG_OutgoingRelationDefinition:
    """Class containing the definition of an outgoing node:

    - `target_base_class: type[BaseNode]`: the target ("to") class of the relationship
    - `target_reference_class: type[BaseNodeReference]`: the reference class of the target class
    - `relation_config: _PG_RelationshipConfigInstantiated`: the configuration model for the relationship
    - `origin_base_class: type[BaseNode]`: the origin ("from") class of the relationship
    """

    target_base_class: type["AbstractBaseNode"]
    target_reference_class: type["BaseNodeReference"]
    relation_config: _PG_RelationshipConfigInstantiated
    origin_base_class: type["AbstractBaseNode"]

    def __hash__(self):
        return hash(
            repr(self.origin_base_class)
            + repr(self.target_base_class)
            + repr(self.relation_config)
        )


@dataclasses.dataclass
class EmbeddedConfig:
    validators: typing.Optional[typing.Sequence[annotated_types.BaseMetadata]] = None


@dataclasses.dataclass
class _EmbeddedConfigInstantiated:
    embedded_node_base: type["AbstractBaseNode"] | type["BaseNonHeritableMixin"] | type[
        "BaseMixin"
    ] | type[types.UnionType]
    validators: typing.Optional[typing.Sequence[annotated_types.BaseMetadata]] = None


@dataclasses.dataclass
class _EmbeddedNodeDefinition:
    embedded_class: type["AbstractBaseNode"] | type["BaseNonHeritableMixin"] | type[
        "BaseMixin"
    ] | type[types.UnionType]
    embedded_config: _EmbeddedConfigInstantiated
