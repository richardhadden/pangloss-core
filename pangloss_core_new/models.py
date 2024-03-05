import uuid

import neo4j.exceptions
from pangloss_core_new.model_setup.base_node_definitions import EditNodeBase

from pangloss_core_new.model_setup.base_node_definitions import (
    AbstractBaseNode,
    ViewNodeBase,
)
from pangloss_core_new.model_setup.model_manager import ModelManager
from pangloss_core_new.database import Transaction, write_transaction, read_transaction
from pangloss_core_new.model_setup.reference_node_base import BaseNodeReference
from pangloss_core_new.cypher_utils import cypher
from pangloss_core_new.exceptions import PanglossNotFoundError, PanglossCreateError


class BaseNode(AbstractBaseNode):
    __abstract__ = True

    def __init_subclass__(cls):
        ModelManager.register_model(cls)
        super().__init_subclass__()

    def __str__(self):
        return f"{self.__class__.__name__}({super().__str__()})"

    @classmethod
    @read_transaction
    async def get_view(cls, tx: Transaction, uid: uuid.UUID) -> ViewNodeBase | None:
        query = cypher.read_query(cls)

        with open("read_query.cypher", "w") as f:
            f.write(query)

        result = await tx.run(query, {"uid": str(uid)})  # type: ignore
        record = await result.value()

        if len(record) == 0:
            raise PanglossNotFoundError(f'<{cls.__name__} uid="{uid}"> not found')

        return cls.View(**record[0])

    @write_transaction
    async def create(self, tx: Transaction) -> BaseNodeReference:
        (
            node_identifier,
            MATCH_CLAUSES,
            CREATE_CLAUSES,
            params_dict,
        ) = cypher.build_write_query_and_params_dict(self)

        query = f"""
        {"""

        """.join(MATCH_CLAUSES)}
        {"""

        """.join(CREATE_CLAUSES)}
        
        
        return {node_identifier}{{.uid, .label, .real_type}}
        """

        with open("write_query.cypher", "w") as f:
            f.write(query)

            f.write(str(params_dict))

        # try:
        # Annoyingly, need override this type hint as Transaction.run takes type LiteralString
        # (not str), which means we cannot dynamically construct the query string
        try:
            result = await tx.run(query, params_dict)  # type:ignore

            record = await result.value()
        except neo4j.exceptions.ConstraintError as e:
            raise PanglossCreateError(e.message)

        # print(record)
        return self.Reference(**record[0])
        # except Exception as e:
        #    print(e)
        #    raise PanglossCreateError(message=e)

    @classmethod
    @read_transaction
    async def get_edit(cls, tx: Transaction, uid: uuid.UUID) -> EditNodeBase:
        # Added some query optimisation: if cls has no outgoing relations or embedded nodes defined,
        # there should be no need to look up these paths.
        # TODO: Further optimisation: if no paths need to be followed at all, there is no need to do this
        # path unpacking business at all!
        query = cypher.read_query(cls)

        with open("read_query.cypher", "w") as f:
            f.write(query)

        result = await tx.run(query, {"uid": str(uid)})  # type: ignore
        record = await result.value()

        if len(record) == 0:
            raise PanglossNotFoundError(f'<{cls.__name__} uid="{uid}"> not found')

        return cls.Edit(**record[0])

    @staticmethod
    @write_transaction
    async def _write_edit(item: EditNodeBase, tx: Transaction) -> None:
        query, params = cypher.update_query(item)
        with open("update_query.cypher", "w") as f:
            f.write(query)
            f.write("\n\n\n\n")
            f.write(str(params))
        result = await tx.run(query, params)  # type: ignore
        record = await result.value()
        if len(record) == 0:
            raise PanglossNotFoundError(
                f'<{item.base_class.__name__} uid="{item.uid}"> not found'
            )
