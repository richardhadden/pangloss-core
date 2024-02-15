from pangloss_core_new.model_setup.setup_utils import (
    __pg_create_embedded_class__,
    __setup_delete_indirect_non_heritable_mixin_fields__,
    __setup_update_embedded_definitions__,
    __setup_update_relation_annotations__,
    __setup_initialise_reference_class__,
)


class ModelManager:
    _registered_models = []

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
            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)

            subclass.embedded_nodes = {}
            __setup_update_embedded_definitions__(subclass)
            subclass.Embedded = __pg_create_embedded_class__(subclass)

            subclass.model_rebuild(force=True, _parent_namespace_depth=depth)
