from pangloss_core_new.model_setup.subnode_proxy import SubNodeProxy
from pangloss_core_new.model_setup.models_base import BaseNodeStandardFields


class BaseNodeReference(BaseNodeStandardFields, SubNodeProxy):
    real_type: str = ""
