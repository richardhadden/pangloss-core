from __future__ import annotations

import typing


from pangloss_core_new.model_setup.models_base import CamelModel

if typing.TYPE_CHECKING:
    from pangloss_core_new.model_setup.base_node_definitions import (
        AbstractBaseNode,
        _EmbeddedNodeDefinition,
        _OutgoingRelationDefinition,
        _OutgoingReifiedRelationDefinition,
    )


class SubNodeProxy(CamelModel):
    """BaseNodes have contained types for View, Edit, Embedded; the contained types should
    be able to access some vital properties of the enclosing class"""

    base_class: typing.ClassVar[type["AbstractBaseNode"]]

    @classmethod
    def _get_model_labels(cls) -> list[str]:
        return cls.base_class._get_model_labels()

    @property
    def property_fields(self) -> dict[str, type]:
        return self.base_class.property_fields

    @property
    def embedded_nodes(self) -> dict[str, "_EmbeddedNodeDefinition"]:
        return self.base_class.embedded_nodes

    @property
    def outgoing_relations(
        self,
    ) -> dict[str, "_OutgoingRelationDefinition | _OutgoingReifiedRelationDefinition"]:
        return self.base_class.outgoing_relations
