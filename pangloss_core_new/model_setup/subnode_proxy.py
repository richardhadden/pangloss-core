from __future__ import annotations

import typing

import pydantic

if typing.TYPE_CHECKING:
    from pangloss_core_new.model_setup.base_node_definitions import (
        AbstractBaseNode,
        _EmbeddedNodeDefinition,
        _OutgoingRelationDefinition,
        _OutgoingReifiedRelationDefinition,
    )


class SubNodeProxy(pydantic.BaseModel):
    """BaseNodes have contained types for View, Edit, Embedded; the contained types should
    be able to access some vital properties of the enclosing class"""

    base_class: typing.ClassVar[type["AbstractBaseNode"]]

    @property
    def embedded_nodes(self) -> dict[str, "_EmbeddedNodeDefinition"]:
        return self.base_class.embedded_nodes

    @property
    def outgoing_relations(
        self,
    ) -> dict[str, "_OutgoingRelationDefinition | _OutgoingReifiedRelationDefinition"]:
        return self.base_class.outgoing_relations
