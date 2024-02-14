from pangloss_core_new.model_setup.base_node_definitions import AbstractBaseNode
from pangloss_core_new.model_setup.model_manager import ModelManager


class BaseNode(AbstractBaseNode):
    __abstract__ = True

    def __init_subclass__(cls):
        ModelManager.register_model(cls)
        super().__init_subclass__()
        # ModelManager.register_model(cls)
