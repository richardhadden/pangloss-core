import uuid

import pydantic

from pangloss_core.model_setup.subnode_proxy import SubNodeProxy
from pangloss_core.model_setup.models_base import BaseNodeStandardFields


class BaseNodeReference(BaseNodeStandardFields, SubNodeProxy):
    uid: uuid.UUID = pydantic.Field(json_schema_extra={"readOnly": False})
    real_type: str = ""
