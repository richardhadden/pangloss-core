import dataclasses
import datetime
import inspect
import types
import typing


import annotated_types
import pydantic

from pangloss_core_new.exceptions import PanglossConfigError
from pangloss_core_new.model_setup.base_node_definitions import (
    EditNodeBase,
    EmbeddedNodeBase,
)

from pangloss_core_new.model_setup.base_node_definitions import (
    AbstractBaseNode,
    BaseMixin,
    BaseNonHeritableMixin,
    ViewNodeBase,
)
from pangloss_core_new.model_setup.config_definitions import (
    EmbeddedConfig,
    _EmbeddedConfigInstantiated,
    _EmbeddedNodeDefinition,
    _IncomingRelationDefinition,
    _IncomingReifiedRelationDefinition,
    _RelationConfigInstantiated,
    _OutgoingRelationDefinition,
    _OutgoingReifiedRelationDefinition,
    RelationConfig,
)
from pangloss_core_new.model_setup.reference_node_base import BaseNodeReference
from pangloss_core_new.model_setup.relation_properties_model import (
    RelationPropertiesModel,
)
from pangloss_core_new.model_setup.relation_to import (
    ReifiedRelation,
    ReifiedTargetConfig,
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


def __setup_model_instantiates_abstract_trait__(
    cls: type[AbstractBaseNode] | type[BaseMixin],
) -> bool:
    # print(cls)
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
        classes,  # type: ignore
        BaseNonHeritableMixin,  # type: ignore
    ) and __setup_model_instantiates_abstract_trait__(
        classes  # type: ignore
    ):
        for cl in classes.__pg_real_types_with_trait__:
            concrete_node_classes += list(_get_concrete_node_classes(cl))

    else:  # Classes is a single class
        if include_subclasses:
            subclasses = _get_all_subclasses(classes, include_abstract=include_abstract)
            concrete_node_classes.extend(subclasses)
        if include_abstract or not classes.__abstract__:  # type: ignore
            concrete_node_classes.append(classes)
    return set(concrete_node_classes)


def __pg_create_embedded_class__(cls: type[AbstractBaseNode]) -> type[EmbeddedNodeBase]:
    """Create an Embedded type for a BaseNode. If it already exists, return existing"""

    if (
        getattr(cls, "Embedded", False)
        and cls.Embedded.__name__ == f"{cls.__name__}Embedded"
    ):
        return cls.Embedded

    parent_fields = {
        field_name: field
        for field_name, field in cls.model_fields.items()
        if field_name != "label"
    }
    embedded_class = pydantic.create_model(
        f"{cls.__name__}Embedded",
        __base__=EmbeddedNodeBase,
        real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
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

            # Not immediately clear why this check is needed; should be set up by ModelManager
            # before running this function. But it seems defining classes out of order results
            # in a state where it has not been set up.
            if not getattr(cls, "embedded_nodes", False):
                cls.embedded_nodes = {}

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

    if not relation_properties_model:
        return cls.Reference
    else:
        reference_model_name = (
            f"{origin_class_name}__{relation_name}__{cls.__name__}Reference"
        )

        new_reference_class = pydantic.create_model(
            reference_model_name,
            __base__=BaseNodeReference,
            base_class=(typing.ClassVar[type["AbstractBaseNode"]], cls),
            real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
            relation_properties=(relation_properties_model, ...),
        )
        return new_reference_class


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


def __setup_update_reified_relation_annotations__(cls: type["AbstractBaseNode"]):
    for field_name, field in cls.model_fields.items():
        if (
            typing.get_args(field.annotation)
            and inspect.isclass(typing.get_args(field.annotation)[0])
            and issubclass(typing.get_args(field.annotation)[0], ReifiedRelation)
        ):
            field.annotation = field.rebuild_annotation()

            reification_class, *other_annotations = typing.get_args(field.annotation)
            reification_class: type[ReifiedRelation] = reification_class
            relation_config = typing.get_args(field.annotation)[1]
            try:
                relation_config: RelationConfig = [
                    item
                    for item in other_annotations
                    if isinstance(item, RelationConfig)
                    and not isinstance(item, ReifiedTargetConfig)
                ][0]

            except IndexError:
                raise PanglossConfigError(
                    f"{cls.__name__}.{field_name} is missing a RelationConfig object)"
                )

            try:
                target_config = [
                    item
                    for item in other_annotations
                    if isinstance(item, ReifiedTargetConfig)
                ][0]
            except IndexError:
                target_config = ReifiedTargetConfig(reverse_name="is_target_of")

            other_annotations = [
                item
                for item in other_annotations
                if not isinstance(item, (RelationConfig, ReifiedTargetConfig))
            ]

            target_class: type["AbstractBaseNode"] = typing.cast(
                type["AbstractBaseNode"],
                reification_class.model_fields["target"].annotation,
            )

            (
                annotated_target_type,
                instantiated_target_config,
            ) = __setup_build_expanded_relation_annotation_type__(
                related_model=target_class,
                relation_config=target_config,
                other_annotations=other_annotations,
                relation_name="target",
                origin_class_name=reification_class.__name__,
            )

            new_reification_model: type[AbstractBaseNode] = typing.cast(
                type[AbstractBaseNode],
                pydantic.create_model(
                    reification_class.__name__,
                    __base__=reification_class,
                    target=(annotated_target_type, ...),
                    outgoing_relations=(
                        typing.ClassVar[
                            dict[
                                str,
                                _OutgoingReifiedRelationDefinition
                                | _OutgoingRelationDefinition,
                            ]
                        ],
                        {},
                    ),
                    embedded_nodes=(
                        typing.ClassVar[dict[str, _EmbeddedNodeDefinition]],
                        {},
                    ),
                    embedded_nodes_instantiated=(typing.ClassVar[bool], False),
                ),
            )
            # TODO: initialise this properly!
            # new_reification_model.__pg_initialise_relations_and_embedded__()

            new_reification_model.__name__ = (
                f"{target_class.__name__}{reification_class.__name__.split(" ")[0]}"
            )

            __setup_update_relation_annotations__(new_reification_model)

            ## TODO: HERE
            new_reification_model.outgoing_relations[
                "target"
            ] = _OutgoingRelationDefinition(
                target_base_class=target_class,
                target_reference_class=target_class,
                relation_config=instantiated_target_config,
                origin_base_class=new_reification_model,
            )

            __setup_update_embedded_definitions__(new_reification_model)
            __setup_add_all_property_fields__(new_reification_model)
            new_reification_model.model_rebuild(force=True)

            # if not reification_class.mro()[1].__annotations__.get("label", False):
            #    del new_reification_model.model_fields["label"]
            #    new_reification_model.model_rebuild(force=True)

            updated_config = _RelationConfigInstantiated(
                **dataclasses.asdict(relation_config),
                relation_to_base=new_reification_model,
            )

            cls.model_fields[field_name] = pydantic.fields.FieldInfo(
                annotation=typing.Annotated[list[new_reification_model], updated_config]  # type: ignore
            )

            cls.outgoing_relations[field_name] = _OutgoingReifiedRelationDefinition(
                target_base_class=new_reification_model,
                relation_config=updated_config,
                origin_base_class=cls,
            )


def __setup_recurse_embeddded_nodes_for_outgoing_types__(
    this_class: type[AbstractBaseNode],
) -> dict[str, _OutgoingRelationDefinition]:
    """Starting from a particular model, work recursively through embedded nodes to find
    outgoing relationships."""
    relations = {}
    for (
        embedded_field_name,
        embedded_node_definition,
    ) in this_class.embedded_nodes.items():
        embedded_classes = _get_concrete_node_classes(
            embedded_node_definition.embedded_class
        )
        for embedded_class in embedded_classes:
            for (
                relation_name,
                relation_definition,
            ) in embedded_class.outgoing_relations.items():
                relations[relation_name] = relation_definition
                for (
                    rel_name,
                    rel,
                ) in __setup_recurse_embeddded_nodes_for_outgoing_types__(
                    embedded_class
                ).items():
                    if not getattr(rel.origin_base_class, "is_embedded_type", False):
                        relations[rel_name] = rel
    return relations


def __setup_add_incoming_relations_to_related_models__(cls: type[AbstractBaseNode]):
    ## TODO: neither of these if statements should ever be true now, but check before removing...

    for (
        relation_name,
        relation_definition,
    ) in {
        # Get outgoing relations for this class, and for all embedded classes
        **cls.outgoing_relations,
        **__setup_recurse_embeddded_nodes_for_outgoing_types__(cls),
    }.items():
        if inspect.isclass(relation_definition.target_base_class) and issubclass(
            relation_definition.target_base_class, ReifiedRelation
        ):
            target_relation_config = [
                item
                for item in typing.get_args(
                    relation_definition.target_base_class.__annotations__["target"]
                )
                if isinstance(item, _RelationConfigInstantiated)
            ][0]

            target_base = target_relation_config.relation_to_base

            for target_base_class in _get_concrete_node_classes(target_base):
                target_base_class.incoming_relations[
                    relation_definition.relation_config.reverse_name
                ].add(
                    _IncomingReifiedRelationDefinition(
                        origin_base_class=cls,
                        origin_reference_class=__setup_create_reference_class__(
                            cls,
                            relation_properties_model=relation_definition.relation_config.relation_model,
                        ),
                        target_base_class=target_base_class,
                        reification_class=typing.cast(
                            type[ReifiedRelation],
                            relation_definition.target_base_class,
                        ),
                        relation_to_reification_config=relation_definition.relation_config,
                        relation_to_target_config=target_relation_config,
                    ),
                )

        else:
            target_base_classes = _get_concrete_node_classes(
                relation_definition.target_base_class
            )

            for target_base_class in target_base_classes:
                # print(cls.__name__, target_base_class.__name__)
                # print(target_base_class)
                target_base_class.incoming_relations[
                    relation_definition.relation_config.reverse_name
                ].add(
                    _IncomingRelationDefinition(
                        origin_base_class=cls,
                        origin_reference_class=__setup_create_reference_class__(
                            cls,
                            relation_properties_model=relation_definition.relation_config.relation_model,
                            relation_name=relation_definition.relation_config.reverse_name,
                            origin_class_name=target_base_class.__name__,
                        ),
                        relation_config=relation_definition.relation_config,
                        target_base_class=target_base_class,
                    )
                )


def __setup_delete_subclassed_relations__(cls: type[AbstractBaseNode]):
    for relation_name, relation_definition in [*cls.outgoing_relations.items()]:
        if relation_definition.relation_config.subclasses_relation:
            if (
                relation_definition.relation_config.subclasses_relation
                not in cls.model_fields
            ):
                raise PanglossConfigError(
                    f"Relation '{cls.__name__}.{relation_name}' "
                    f"is trying to subclass the relation "
                    f"'{relation_definition.relation_config.subclasses_relation}', but this "
                    f"does not exist on any parent class of '{cls.__name__}'"
                )

            del cls.model_fields[
                relation_definition.relation_config.subclasses_relation
            ]

            del cls.outgoing_relations[
                relation_definition.relation_config.subclasses_relation
            ]
            # cls.model_rebuild(force=True)
            relation_definition.relation_config.relation_labels.add(
                relation_definition.relation_config.subclasses_relation
            )

        for cl in cls.mro():
            if cl is AbstractBaseNode:
                break
            if issubclass(cl, AbstractBaseNode):
                if (
                    relation_definition.relation_config.subclasses_relation
                    in cl.model_fields
                ):
                    # TODO: no idea what this 'extra_label' variable is for
                    # extra_label = cl.outgoing_relations[
                    #    relation_definition.relation_config.subclasses_relation
                    # ].relation_config.relation_labels
                    # print("extra label")
                    relation_definition.relation_config.relation_labels.update(
                        cl.outgoing_relations[
                            relation_definition.relation_config.subclasses_relation
                        ].relation_config.relation_labels
                    )
    # print("MODEL FIELDS", cls.model_fields.keys())
    cls.model_rebuild(force=True)


def __setup_add_all_property_fields__(cls: type[AbstractBaseNode]) -> None:
    property_fields = {}

    for field_name, field in cls.model_fields.items():
        # print(field)
        if (
            field_name not in cls.outgoing_relations
            and field_name not in cls.embedded_nodes
            and field_name != "real_type"
        ):
            property_fields[field_name] = field
    cls.property_fields = property_fields


def __setup_construct_view_type__(cls: type[AbstractBaseNode]):
    """Constructs a view type on the class."""
    # print(cls.__name__, cls.incoming_relations)
    incoming_model_fields = {}

    for (
        incoming_relation_name,
        incoming_relation_definitions,
    ) in cls.incoming_relations.items():
        incoming_related_types: list[type[BaseNodeReference]] = []
        for incoming_relation in incoming_relation_definitions:
            incoming_related_types.append(incoming_relation.origin_reference_class)
        incoming_model_fields[incoming_relation_name] = (
            typing.Optional[list[typing.Union[*tuple(incoming_related_types)]]],  # type: ignore
            None,
        )

    view_model = pydantic.create_model(
        f"{cls.__name__}View",
        __base__=ViewNodeBase,
        is_view_model=(
            typing.ClassVar[bool],
            True,
        ),
        **incoming_model_fields,
        real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
        base_class=(typing.ClassVar[type[AbstractBaseNode]], cls),
    )

    view_model.model_fields = {
        **view_model.model_fields,
        **cls.model_fields,
    }
    view_model.model_rebuild(force=True)
    cls.View = view_model  # type: ignore


def __setup_find_cyclic_outgoing_references_for_edit__(cls: type[AbstractBaseNode]):
    cyclic = set()
    for relation_name, relation in cls.outgoing_relations.items():
        if relation.relation_config.edit_inline:
            for concrete_related_type in _get_concrete_node_classes(
                relation.target_base_class, include_subclasses=True
            ):  # Get all the possible related types
                if concrete_related_type == cls:  # Self reference
                    cyclic.add(concrete_related_type)
                else:
                    for (
                        inner_relation_name,
                        inner_relation,
                    ) in concrete_related_type.outgoing_relations.items():
                        for inner_concrete_related_type in _get_concrete_node_classes(
                            inner_relation.target_base_class, include_subclasses=True
                        ):
                            if inner_concrete_related_type in cyclic:
                                return cyclic
                            if inner_concrete_related_type == cls or issubclass(
                                inner_concrete_related_type, cls
                            ):
                                # print("adding", inner_concrete_related_type)
                                cyclic.add(inner_concrete_related_type)

                            else:
                                # print("recurse on", inner_concrete_related_type)
                                cyclic.update(
                                    __setup_find_cyclic_outgoing_references_for_edit__(
                                        inner_concrete_related_type
                                    )
                                )

    return cyclic


def __setup_construct_edit_type__(cls: type[AbstractBaseNode]):
    if getattr(cls, "Edit", False) and cls.Edit.__name__ == f"{cls.__name__}Edit":
        return cls.Edit
    outgoing_relation_new_defs = {}
    for relation_name, relation in cls.outgoing_relations.items():
        if relation.relation_config.edit_inline:
            all_related_types = set()

            for concrete_related_type in _get_concrete_node_classes(
                relation.target_base_class, include_subclasses=True
            ):
                if (
                    concrete_related_type
                    in __setup_find_cyclic_outgoing_references_for_edit__(cls)
                ):
                    all_related_types.add(f"{concrete_related_type.__name__}Edit")
                else:
                    m = __setup_construct_edit_type__(concrete_related_type)

                    all_related_types.add(m)

            outgoing_relation_new_defs[relation_name] = (
                typing.Annotated[
                    list[typing.Union[*tuple(all_related_types)]],  # type: ignore
                    relation.relation_config.validators,
                    relation.relation_config,
                ],
                pydantic.Field(default_factory=list, discriminator="real_type"),
            )

        else:
            # print(typing.get_args(cls.model_fields[relation_name].annotation))
            all_related_types = []
            for ann in typing.get_args(cls.model_fields[relation_name].annotation):
                all_related_types.append(ann)

            all_related_types = tuple(all_related_types)
            outgoing_relation_new_defs[relation_name] = (
                typing.Annotated[
                    list[typing.Union[*all_related_types]],  # type: ignore
                    relation.relation_config.validators,
                    relation.relation_config,
                ],
                pydantic.Field(default_factory=list, discriminator="real_type"),
            )
    embedded_new_defs = {}

    for embedded_name, embedded_definition in cls.embedded_nodes.items():
        all_embedded_types = set()
        for concrete_embedded_type in _get_concrete_node_classes(
            embedded_definition.embedded_class, include_subclasses=True
        ):
            all_embedded_types.add(concrete_embedded_type.Embedded)

        embedded_new_defs[embedded_name] = (
            typing.Annotated[
                list[typing.Union[*all_embedded_types]],  # type: ignore
                embedded_definition.embedded_config.validators,
                embedded_definition.embedded_config,
            ],
            pydantic.Field(default_factory=list, discriminator="real_type"),
        )

    edit_model = pydantic.create_model(
        f"{cls.__name__}Edit",
        __base__=EditNodeBase,
        is_view_model=(
            typing.ClassVar[bool],
            True,
        ),
        real_type=(typing.Literal[cls.__name__.lower()], cls.__name__.lower()),  # type: ignore
        base_class=(typing.ClassVar[AbstractBaseNode], cls),
        **outgoing_relation_new_defs,
        **embedded_new_defs,
    )

    for property_name, property in cls.property_fields.items():
        edit_model.model_fields[property_name] = property  # type: ignore

    for k, v in edit_model.model_fields.items():
        v = v.rebuild_annotation()

    cls.Edit = edit_model

    return edit_model
