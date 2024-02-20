from collections import defaultdict

from pangloss_core_new.exceptions import PanglossConfigError
from pangloss_core_new.model_setup.setup_utils import (
    __pg_create_embedded_class__,
    __setup_delete_indirect_non_heritable_mixin_fields__,
    __setup_update_embedded_definitions__,
    __setup_update_relation_annotations__,
    __setup_initialise_reference_class__,
    __setup_update_reified_relation_annotations__,
    __setup_add_incoming_relations_to_related_models__,
    __setup_delete_subclassed_relations__,
    __setup_add_all_property_fields__,
    __setup_construct_view_type__,
    __setup_construct_edit_type__,
)


class ModelManager:
    _registered_models = []

    def __init__(self, *args, **kwargs):
        raise PanglossConfigError("Model Manager cannot be initialised")

    @classmethod
    def register_model(cls, model):
        cls._registered_models.append(model)

    @classmethod
    def _reset(cls):
        cls._registered_models = []

    @classmethod
    def initialise_models(cls, depth=2):
        for subclass in cls._registered_models:
            print("Initialising", subclass.__name__)

            __setup_delete_indirect_non_heritable_mixin_fields__(subclass)
            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)

            subclass.outgoing_relations = {}
            __setup_update_relation_annotations__(subclass)
            __setup_update_reified_relation_annotations__(subclass)
            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)
            __setup_delete_subclassed_relations__(subclass)
            subclass.embedded_nodes = {}
            __setup_update_embedded_definitions__(subclass)
            subclass.Embedded = __pg_create_embedded_class__(subclass)

            subclass.incoming_relations = defaultdict(set)
            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)

        for subclass in cls._registered_models:
            __setup_add_incoming_relations_to_related_models__(subclass)
            __setup_add_all_property_fields__(subclass)
            # __setup_initialise_reference_class__(subclass)

        for subclass in cls._registered_models:
            __setup_construct_view_type__(subclass)
            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)
            __setup_construct_edit_type__(subclass)
