import inspect
import typing

from pangloss_core_new.exceptions import PanglossConfigError
from pangloss_core_new.model_setup.config_definitions import (
    _EmbeddedNodeDefinition,
    _IncomingRelationDefinition,
    _IncomingReifiedRelationDefinition,
    _OutgoingRelationDefinition,
    _OutgoingReifiedRelationDefinition,
)
from pangloss_core_new.model_setup.models_base import BaseNodeStandardFields
from pangloss_core_new.model_setup.subnode_proxy import SubNodeProxy
from pangloss_core_new.model_setup.reference_node_base import BaseNodeReference


class EmbeddedNodeBase(SubNodeProxy):
    real_type: str


class ViewNodeBase(SubNodeProxy):
    pass


class EditNodeBase(SubNodeProxy):
    pass


class BaseNonHeritableMixin:
    __pg_real_types_with_trait__: set[type["AbstractBaseNode"]]

    @classmethod
    def __pg_is_subclass_of_trait__(cls):
        """Determine whether a class is a subclass of AbstractTrait,
        not the application of a trait to a real BaseNode class.

        This should work by not having BaseNode in its class hierarchy
        """
        for parent in cls.mro()[1:]:
            if issubclass(parent, AbstractBaseNode):
                return False
        else:
            return True

    def __init_subclass__(cls):
        cls.__pg_real_types_with_trait__ = set()


class BaseMixin:
    pass


class AbstractBaseNode(BaseNodeStandardFields):
    __abstract__ = True

    View: typing.ClassVar[type["ViewNodeBase"]]
    Embedded: typing.ClassVar[type["EmbeddedNodeBase"]]
    Edit: typing.ClassVar[type["EditNodeBase"]]
    Reference: typing.ClassVar[type["BaseNodeReference"]]

    embedded_nodes: typing.ClassVar[dict[str, _EmbeddedNodeDefinition]]
    embedded_nodes_instantiated: typing.ClassVar[bool] = False

    # real_type: str = pydantic.Field(default_factory=)
    outgoing_relations: typing.ClassVar[
        dict[str, _OutgoingReifiedRelationDefinition | _OutgoingRelationDefinition]
    ]

    incoming_relations: typing.ClassVar[
        dict[str, set[_IncomingRelationDefinition | _IncomingReifiedRelationDefinition]]
    ]

    property_fields: typing.ClassVar[dict[str, type]]

    def __init_subclass__(cls):
        cls.__setup_run_init_subclass_checks__()
        cls.__pg_add_type_to_trait_list_of_real_types__()

        cls.__abstract__ = cls.__dict__.get("__abstract__", False)

        cls.model_rebuild(force=True)

    @classmethod
    def _get_model_labels(cls) -> list[str]:
        """All neo4j labels for model.

        Includes direct Trait names."""
        return [
            c.__name__
            for c in cls.mro()
            if (
                (issubclass(c, AbstractBaseNode))
                or c in cls.__pg_get_non_heritable_mixins_as_direct_ancestors__()
            )
            and c is not AbstractBaseNode
        ]

    @classmethod
    def __pg_add_type_to_trait_list_of_real_types__(cls):
        if issubclass(cls, BaseNonHeritableMixin):
            for trait in cls.__pg_get_non_heritable_mixins_as_direct_ancestors__():
                trait.__pg_real_types_with_trait__.add(cls)

    @classmethod
    def __pg_get_non_heritable_mixins_as_direct_ancestors__(
        cls,
    ) -> set[BaseNonHeritableMixin]:
        """Identifies Traits that are directly applied to a model class"""
        traits_as_direct_bases = []
        for base in cls.__bases__:
            for parent in inspect.getmro(base):
                if parent is AbstractBaseNode:
                    break
                elif parent is BaseNonHeritableMixin:
                    traits_as_direct_bases.append(base)
                else:
                    continue
        return set(traits_as_direct_bases)

    @classmethod
    def __pg_get_non_heritable_mixins_as_indirect_ancestors__(
        cls,
    ) -> set[BaseNonHeritableMixin]:
        traits_as_indirect_ancestors = []
        traits_as_direct_ancestors = (
            cls.__pg_get_non_heritable_mixins_as_direct_ancestors__()
        )
        for c in cls.mro():
            if (
                issubclass(c, BaseNonHeritableMixin)
                and not issubclass(c, AbstractBaseNode)
                and c is not BaseNonHeritableMixin
                and c is not cls
                and c not in traits_as_direct_ancestors
            ):
                traits_as_indirect_ancestors.append(c)
        return set(traits_as_indirect_ancestors)

    @classmethod
    def __setup_run_init_subclass_checks__(cls):
        """Run checks on subclasses for validity, following rules below.

        1. Cannot have field named `relation_properties` as this is used internally
        2. Cannot have 'Embedded' in class name"""

        for field_name, field in cls.model_fields.items():
            if field_name == "relation_properties":
                raise PanglossConfigError(
                    f"Field 'relation_properties' (on model {cls.__name__}) is a reserved name. Please rename this field."
                )

        if "Embedded" in cls.__name__:
            raise PanglossConfigError(
                f"Base models cannot use 'Embedded' as part of the name, as this is used "
                f"internally. (Model '{cls.__name__}' should be renamed)"
            )
