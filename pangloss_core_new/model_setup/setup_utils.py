import dataclasses
import types
import typing

import annotated_types
import pydantic

from pangloss_core_new.exceptions import PanglossConfigError
from pangloss_core_new.model_setup.base_node_definitions import (
    AbstractBaseNode,
    BaseMixin,
    BaseNonHeritableMixin,
    EmbeddedNodeBase,
)
from pangloss_core_new.model_setup.config_definitions import (
    EmbeddedConfig,
    _EmbeddedConfigInstantiated,
    _EmbeddedNodeDefinition,
    _RelationConfigInstantiated,
    _OutgoingRelationDefinition,
    RelationConfig,
)
from pangloss_core_new.model_setup.reference_node_base import BaseNodeReference
from pangloss_core_new.model_setup.relation_properties_model import (
    RelationPropertiesModel,
)


def _get_all_subclasses(
    cls, include_abstract: bool = False
) -> set[type[AbstractBaseNode]]:
    subclasses = []
    for subclass in cls.__subclasses__():
        if not subclass.__abstract__ or include_abstract:
            subclasses += [subclass, *_get_all_subclasses(subclass)]
        else:
            subclasses += _get_all_subclasses(subclass)
    return set(subclasses)


def __pg_model_instantiates_abstract_trait__(
    cls: type[AbstractBaseNode] | type[BaseMixin],
) -> bool:
    """Determines whether a Node model is a direct instantiation of a trait."""
    return issubclass(cls, BaseNonHeritableMixin) and cls.__pg_is_subclass_of_trait__()


def _get_concrete_node_classes(
    classes: type[AbstractBaseNode]
    | type[BaseNonHeritableMixin]
    | type[BaseMixin]
    | type[types.UnionType],
    include_subclasses: bool = False,
    include_abstract: bool = False,
) -> set[type[AbstractBaseNode]]:
    """Given a BaseNode, AbstractTrait or Union type, returns set of concrete BaseNode types.

    By default, does not include subclasses of types or abstract classes.
    """

    concrete_node_classes = []
    if unpacked_classes := typing.get_args(classes):
        for cl in unpacked_classes:
            concrete_node_classes += list(
                _get_concrete_node_classes(
                    cl,
                    include_subclasses=include_subclasses,
                    include_abstract=include_abstract,
                )
            )
    elif issubclass(
        classes, BaseNonHeritableMixin
    ) and __pg_model_instantiates_abstract_trait__(
        classes  # type: ignore
    ):
        for cl in classes.__pg_real_types_with_trait__:
            concrete_node_classes += list(_get_concrete_node_classes(cl))

    else:  # Classes is a single class
        concrete_node_classes.append(classes)
        if include_subclasses:
            subclasses = _get_all_subclasses(classes, include_abstract=include_abstract)
            concrete_node_classes.extend(subclasses)
        if include_abstract or not classes.__abstract__:  # type: ignore
            concrete_node_classes.append(classes)

    # concrete_node_classes = [
    #    concrete_node_class
    #    for concrete_node_class in concrete_node_classes
    #
    #     # and not getattr(concrete_node_class, "is_embedded_type", False)
    # ]
    return set(concrete_node_classes)


def __pg_create_embedded_class__(cls: type[AbstractBaseNode]) -> type[EmbeddedNodeBase]:
    """Create an Embedded type for a BaseNode. If it already exists, return existing"""
    if hasattr(cls, "Embedded"):
        return cls.Embedded

    parent_fields = {
        field_name: field
        for field_name, field in cls.model_fields.items()
        if field_name != "label"
    }
    embedded_class = pydantic.create_model(
        f"{cls.__name__}Embedded",
        __base__=EmbeddedNodeBase,
        real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),
    )
    embedded_class.base_class = cls
    embedded_class.model_fields.update(parent_fields)
    embedded_class.model_rebuild(force=True)
    cls.Embedded = embedded_class
    return embedded_class


def __setup_update_embedded_definitions__(cls: type[AbstractBaseNode]) -> None:
    if cls.embedded_nodes_instantiated:
        return

    for field_name, field in cls.model_fields.items():
        annotation = field.rebuild_annotation()

        if typing.get_args(annotation) and (
            getattr(typing.get_args(annotation)[0], "__name__", False) == "Embedded"
            or getattr(annotation, "__name__", False) == "Embedded"
        ):
            embedded_wrapper, *other_annotations = typing.get_args(annotation)

            try:
                # If the class we are looking at is a BaseNode itself,
                # then cool
                if issubclass(embedded_wrapper, (AbstractBaseNode)):
                    embedded_base_type = embedded_wrapper
            except TypeError:
                # Otherwise, we need to unpack it from Annotated

                if isinstance(embedded_wrapper, types.UnionType):
                    embedded_base_type = embedded_wrapper
                else:
                    embedded_base_type = embedded_wrapper.__args__[0]  # type: ignore

            if not embedded_base_type:
                raise PanglossConfigError(
                    f"Something went wrong with an Embedded node on {cls.__name__}.{field_name}"
                )

            embedded_base_type = typing.cast(
                type[AbstractBaseNode]
                | type[BaseMixin]
                | type[BaseNonHeritableMixin]
                | type[types.UnionType],
                embedded_base_type,
            )

            try:
                embedded_config: EmbeddedConfig | None = [
                    item
                    for item in other_annotations
                    if isinstance(item, EmbeddedConfig)
                ][0]
                other_annotations = [
                    item
                    for item in other_annotations
                    if not isinstance(item, EmbeddedConfig)
                ]
            except IndexError:
                # We don't need to have either embedded_config or other annotations
                embedded_config: EmbeddedConfig | None = None
                other_annotations = []

            annotation, updated_config = __pg_build_embedded_annotation_type__(
                embedded_node_type=embedded_base_type,
                embedded_config=embedded_config,
                other_annotations=other_annotations,
            )

            cls.model_fields[field_name] = pydantic.fields.FieldInfo(
                annotation=annotation
            )

            cls.embedded_nodes[field_name] = _EmbeddedNodeDefinition(
                embedded_class=updated_config.embedded_node_base,
                embedded_config=updated_config,
            )
            cls.embedded_nodes_instantiated = True


def __pg_build_embedded_annotation_type__(
    embedded_node_type: type[AbstractBaseNode]
    | type[BaseNonHeritableMixin]
    | type[BaseMixin]
    | type[types.UnionType],
    embedded_config: EmbeddedConfig | None,
    other_annotations: list[typing.Any],
) -> tuple[typing.Any, _EmbeddedConfigInstantiated]:
    embedded_node_config: EmbeddedConfig = embedded_config or EmbeddedConfig(
        validators=[annotated_types.MinLen(1), annotated_types.MaxLen(1)]
    )

    embedded_node_config_instantiated: _EmbeddedConfigInstantiated = (
        _EmbeddedConfigInstantiated(
            embedded_node_base=embedded_node_type,
            **dataclasses.asdict(embedded_node_config),
        )
    )

    validators = (
        embedded_node_config.validators if embedded_node_config.validators else []
    )

    embedded_node_embedded_types = []
    for concrete_embedded_type in _get_concrete_node_classes(
        embedded_node_type, include_subclasses=True
    ):
        __setup_update_embedded_definitions__(concrete_embedded_type)

        new_embedded_model = __pg_create_embedded_class__(concrete_embedded_type)

        embedded_node_embedded_types.append(new_embedded_model)

    return (
        typing.Annotated[
            list[typing.Union[*embedded_node_embedded_types]],  # type: ignore
            *validators,
            *other_annotations,
            embedded_node_config_instantiated,
        ],
        embedded_node_config_instantiated,
    )


def __setup_update_relation_annotations__(cls: type["AbstractBaseNode"]):
    for field_name, field in cls.model_fields.items():
        # Relation fields can be defined as either a typing.Annotated (including metadata)

        field.annotation = field.rebuild_annotation()

        if (
            typing.get_args(field.annotation)
            and getattr(typing.get_args(field.annotation)[0], "__name__", False)
            == "RelationTo"
        ):
            relation_wrapper, *other_annotations = typing.get_args(field.annotation)
            related_base_type: type["AbstractBaseNode"] = relation_wrapper.__args__[0]

            try:
                relation_config: RelationConfig = [
                    item
                    for item in other_annotations
                    if isinstance(item, RelationConfig)
                ][0]
                other_annotations = [
                    item
                    for item in other_annotations
                    if not isinstance(item, RelationConfig)
                ]
            except IndexError:
                raise PanglossConfigError(
                    f"{cls.__name__}.{field_name} is missing a RelationConfig object)"
                )

            (
                annotation,
                updated_config,
            ) = __setup_build_expanded_relation_annotation_type__(
                related_model=related_base_type,
                relation_config=relation_config,
                other_annotations=other_annotations,
                origin_class_name=cls.__name__,
                relation_name=field_name,
            )
            cls.model_fields[field_name] = pydantic.fields.FieldInfo(
                annotation=annotation
            )

            cls.outgoing_relations[field_name] = _OutgoingRelationDefinition(
                target_base_class=updated_config.relation_to_base,
                target_reference_class=updated_config.relation_to_base,  # type: ignore
                relation_config=updated_config,
                origin_base_class=cls,
            )


def __setup_build_expanded_relation_annotation_type__(
    related_model: type[AbstractBaseNode],
    relation_config: RelationConfig,
    other_annotations: list[typing.Any],
    relation_name: str,
    origin_class_name: str,
) -> tuple[typing.Any, _RelationConfigInstantiated]:
    """Expands an annotation to include subclasses/classes from AbstractTrait, etc."""

    validators = relation_config.validators if relation_config.validators else []

    concrete_related_types = _get_concrete_node_classes(
        related_model, include_subclasses=True
    )

    all_related_types = []
    instantiated_relation_config = _RelationConfigInstantiated(
        relation_to_base=related_model,
        **dataclasses.asdict(relation_config),  # type: ignore
    )
    for concrete_related_type in concrete_related_types:
        if relation_config.create_inline:
            all_related_types.append(concrete_related_type)
        else:
            all_related_types.append(
                __setup_create_reference_class__(
                    concrete_related_type,
                    relation_name,
                    origin_class_name,
                    relation_properties_model=instantiated_relation_config.relation_model,
                )
            )

    all_related_types = tuple(all_related_types)

    return (
        typing.Annotated[
            list[typing.Union[*all_related_types]],  # type: ignore
            *validators,
            *other_annotations,
            instantiated_relation_config,
        ],
        instantiated_relation_config,
    )


def __setup_initialise_reference_class__(cls):
    if getattr(cls, "Reference", None):
        cls.Reference = pydantic.create_model(
            f"{cls.__name__}Reference",
            __base__=cls.Reference,
            base_class=(typing.ClassVar[type["AbstractBaseNode"]], cls),
            real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
        )
    else:
        cls.Reference = pydantic.create_model(
            f"{cls.__name__}Reference",
            __base__=BaseNodeReference,
            base_class=(typing.ClassVar[type["AbstractBaseNode"]], cls),
            real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
        )


def __setup_create_reference_class__(
    cls: type[AbstractBaseNode],
    relation_name: str | None = None,
    origin_class_name: str | None = None,
    relation_properties_model: type[RelationPropertiesModel] | None = None,
) -> type[BaseNodeReference]:
    if not getattr(cls, "Reference", None) or not cls.Reference.base_class == cls:
        __setup_initialise_reference_class__(cls)
    print(cls.Reference)
    if not relation_properties_model:
        return cls.Reference
    else:
        return pydantic.create_model(
            f"{origin_class_name}__{relation_name}__{cls.__name__}Reference",
            __base__=BaseNodeReference,
            base_class=(typing.ClassVar[type["AbstractBaseNode"]], cls),
            real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
            relation_properties=(relation_properties_model, ...),
        )


def __setup_delete_indirect_non_heritable_mixin_fields__(
    cls: type[AbstractBaseNode],
) -> None:
    trait_fields_to_delete = set()
    for trait in cls.__pg_get_non_heritable_mixins_as_indirect_ancestors__():
        for field_name in cls.model_fields:
            # AND AND... not in the parent class annotations that is *not* a trait...
            if field_name in trait.__annotations__ and trait not in cls.__annotations__:
                trait_fields_to_delete.add(field_name)
    for td in trait_fields_to_delete:
        del cls.model_fields[td]


def __setup_run_init_subclass_checks__(cls: type[AbstractBaseNode]):
    """Run checks on subclasses for validity, following rules below.

    1. Cannot have field named `relation_properties` as this is used internally
    2. Cannot have 'Embedded' in class name"""
    print(cls)
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
