from __future__ import annotations

import secrets
import typing
import uuid
from typing import Any


if typing.TYPE_CHECKING:
    from pangloss_core_new.model_setup.base_node_definitions import (
        EditNodeBase,
        AbstractBaseNode,
    )

from pangloss_core_new.model_setup.base_node_definitions import EmbeddedNodeBase
from pangloss_core_new.model_setup.relation_to import ReifiedRelation


def get_unique_string():
    return "x" + uuid.uuid4().hex[:6].lower()


def labels_to_query_labels(
    node: AbstractBaseNode | type[AbstractBaseNode] | type[EditNodeBase],
    extra_labels: list[str] | None = None,
) -> str:
    try:
        labels = node._get_model_labels()
    except:
        labels = node.base_class._get_model_labels()

    if extra_labels:
        labels.extend(extra_labels)
    return ":" + ":".join(labels)


def convert_type_for_writing(value):
    match value:
        case uuid.UUID():
            return str(value)
        case set():
            return list(value)
        case _:
            return value


def unpack_properties_to_create_props_and_param_dict(
    node: AbstractBaseNode,
) -> tuple[str, dict[str, Any]]:
    q_pairs = []
    params = {}

    for prop_name, field in node.property_fields.items():
        try:
            param_id = get_unique_string()
            params[param_id] = convert_type_for_writing(getattr(node, prop_name))
            q_pairs.append(f"""{prop_name}: ${param_id}""")
        except AttributeError as e:
            if isinstance(node, EmbeddedNodeBase) and prop_name == "label":
                pass
            else:
                raise AttributeError(e)

    real_type_id = get_unique_string()
    params[real_type_id] = (
        node.__class__.__name__.replace("Embedded", "").replace("Edit", "").lower()
    )
    q_pairs.append(f"""real_type: ${real_type_id}""")
    return "{" + ", ".join(q_pairs) + "}", params


def unpack_dict_to_cypher_map_and_params(d):
    q_pairs = []
    params = {}
    for key, value in d.items():
        param_id = get_unique_string()
        params[param_id] = convert_type_for_writing(value)
        q_pairs.append(f"""{key}: ${param_id}""")
    return "{" + ", ".join(q_pairs) + "}", params


def build_write_query_and_params_dict_for_single_node(
    node: AbstractBaseNode,
) -> tuple[str, str, dict[str, Any]]:
    labels = labels_to_query_labels(node)
    (
        node_props,
        params_dict,
    ) = unpack_properties_to_create_props_and_param_dict(node)

    node_identifier = get_unique_string()

    query = f"""
    
    CREATE ({node_identifier}{labels_to_query_labels(node)} {node_props})
    
    """
    return node_identifier, query, params_dict


def build_write_query_for_related_node(
    current_node_identifier: str,
    related_node: AbstractBaseNode,
    relation_label: str,
    relation_properties: dict,
) -> tuple[list[str], list[str], dict[str, Any]]:
    related_node_identifier = get_unique_string()
    uid_param = get_unique_string()

    (
        relation_properties_cypher,
        relation_properties_params,
    ) = unpack_dict_to_cypher_map_and_params(relation_properties)

    MATCH_CLAUSES = [f"MATCH ({related_node_identifier} {{uid: ${uid_param}}})"]
    CREATE_CLAUSES = [
        f"CREATE ({current_node_identifier})-[:{relation_label.upper()} {relation_properties_cypher}]->({related_node_identifier})"
    ]

    return (
        MATCH_CLAUSES,
        CREATE_CLAUSES,
        {
            **relation_properties_params,
            uid_param: convert_type_for_writing(related_node.uid),
        },
    )


def build_write_query_and_params_dict(
    node: AbstractBaseNode, extra_labels: list[str] | None = None
) -> tuple[str, list[str], list[str], dict[str, Any]]:
    labels = labels_to_query_labels(node)
    (
        node_props,
        params_dict,
    ) = unpack_properties_to_create_props_and_param_dict(node)

    node_identifier = get_unique_string()

    CREATE_CLAUSES = [
        f"CREATE ({node_identifier}{labels_to_query_labels(node, extra_labels=extra_labels)} {node_props})"
    ]
    MATCH_CLAUSES = []

    for embedded_name, embedded_definition in node.embedded_nodes.items():
        for embedded_node in getattr(node, embedded_name):
            (
                embedded_node_identifier,
                embedded_query_match_clauses,
                embedded_query_create_clauses,
                embedded_params_dict,
            ) = build_write_query_and_params_dict(
                embedded_node, extra_labels=["Embedded"]
            )
            CREATE_CLAUSES += [
                *embedded_query_create_clauses,
                f"CREATE ({node_identifier})-[:{embedded_name.upper()}]->({embedded_node_identifier})",
            ]
            MATCH_CLAUSES += embedded_query_match_clauses

            params_dict = {**params_dict, **embedded_params_dict}

    for relation_name, relation in node.outgoing_relations.items():
        if issubclass(relation.target_base_class, ReifiedRelation):
            for related_reification in getattr(node, relation_name):
                (
                    reified_node_identifier,
                    reified_query_match_clauses,
                    reified_query_create_clauses,
                    reified_params_dict,
                ) = build_write_query_and_params_dict(related_reification)

                relation_dict = {
                    "reverse_name": relation.relation_config.reverse_name,
                    "relation_labels": relation.relation_config.relation_labels,
                    # **dict(related_reification.relation_properties),
                }

                (
                    relation_properties_cypher,
                    relation_properties_params,
                ) = unpack_dict_to_cypher_map_and_params(relation_dict)

                CREATE_CLAUSES += [
                    *reified_query_create_clauses,
                    f"CREATE ({node_identifier})-[:{relation_name.upper()} {relation_properties_cypher}]->({reified_node_identifier})",
                ]
                MATCH_CLAUSES += reified_query_match_clauses
                params_dict = {
                    **params_dict,
                    **reified_params_dict,
                    **relation_properties_params,
                }
        elif relation.relation_config.create_inline:
            for related_item in getattr(node, relation_name):
                extra_labels = ["CreateInline", "ReadInline"]
                if relation.relation_config.edit_inline:
                    extra_labels.append("EditInline")
                if relation.relation_config.delete_related_on_detach:
                    extra_labels.append("DeleteDetach")
                (
                    related_node_identifier,
                    query_match_clauses,
                    query_create_clauses,
                    query_params_dict,
                ) = build_write_query_and_params_dict(
                    related_item, extra_labels=extra_labels
                )

                CREATE_CLAUSES += [
                    *query_create_clauses,
                    f"CREATE ({node_identifier})-[:{relation_name.upper()}]->({related_node_identifier})",
                ]
                MATCH_CLAUSES += query_match_clauses
                params_dict = {**params_dict, **query_params_dict}

        else:
            for related_item in getattr(node, relation_name):
                relation_dict = {
                    "reverse_name": relation.relation_config.reverse_name,
                    "relation_labels": relation.relation_config.relation_labels,
                    **dict(getattr(related_item, "relation_properties", {})),
                }

                (
                    related_node_match_clauses,
                    related_node_create_clauses,
                    related_node_params,
                ) = build_write_query_for_related_node(
                    current_node_identifier=node_identifier,
                    related_node=related_item,
                    relation_label=relation_name,
                    relation_properties=relation_dict,
                )
                params_dict = {**params_dict, **related_node_params}
                MATCH_CLAUSES += related_node_match_clauses
                CREATE_CLAUSES += related_node_create_clauses

    # for embedded_node_name, embedded_node_definition in node.embedded_nodes.items():
    #    for embedded_node in getattr(node, rel)

    return node_identifier, MATCH_CLAUSES, CREATE_CLAUSES, params_dict


def read_query(cls: type[AbstractBaseNode]):
    label = cls.__name__
    query = f"""
        
        MATCH path_to_node = (node:{label} {{uid: $uid}})
        
        CALL {{
            WITH node, path_to_node
            {"""OPTIONAL MATCH path_to_direct_nodes = (node)-[]->(:BaseNode)""" if cls.outgoing_relations else ""}
            OPTIONAL MATCH path_through_read_nodes = (node)-[]->(:ReadInline)((:ReadInline)-[]->(:ReadInline)){{0,}}(:ReadInline)-[]->{{0,}}(:BaseNode)
            {"""OPTIONAL MATCH path_to_related_through_embedded = (node)-[]->(:Embedded)((:Embedded)-[]->(:Embedded)){ 0, }(:Embedded)-[]->{0,}(:BaseNode)""" if cls.embedded_nodes else ""}
            OPTIONAL MATCH path_to_reified = (node)-[]->(:ReifiedRelation)-[]->(:BaseNode)
            WITH apoc.coll.flatten([
                {"collect(path_to_direct_nodes)," if cls.outgoing_relations else ""}
                {"collect(path_to_related_through_embedded)," if cls.embedded_nodes else ""}
                collect(path_through_read_nodes),
                collect(path_to_node),
                collect(path_to_reified)
            ]) AS paths, node
            CALL apoc.convert.toTree(paths)
            YIELD value
            RETURN value as value
        }}
        {
        """WITH node, value
        CALL {
            WITH node
            CALL {
                WITH node
                OPTIONAL MATCH (node)<-[reverse_relation]-(x WHERE (x:Embedded OR x:ReifiedRelation))(()<--()){ 0, }()<--(related_node)
                WHERE NOT related_node:Embedded AND NOT related_node:ReifiedRelation
                WITH reverse_relation.reverse_name AS reverse_relation_type, collect(related_node{ .uid, .label, .real_type }) AS related_node_data
                RETURN collect({ t: reverse_relation_type, related_node_data: related_node_data }) AS via_intermediate
            }
            CALL {
                WITH node
                MATCH (node)<-[reverse_relation]-(related_node:BaseNode)
                WHERE NOT related_node:Embedded AND NOT related_node:ReifiedRelation
                WITH reverse_relation.reverse_name AS reverse_relation_type, collect(related_node{ .uid, .label, .real_type }) AS related_node_data
                RETURN collect({ t: reverse_relation_type, related_node_data: related_node_data }) AS direct_incoming
            }
            RETURN REDUCE(s = { }, item IN apoc.coll.flatten([direct_incoming, via_intermediate]) | apoc.map.setEntry(s, item.t, item.related_node_data)) AS reverse_relations
        }

        WITH value, node, reverse_relations
        RETURN apoc.map.mergeList([node, reverse_relations, value])""" if cls.incoming_relations else """ RETURN value """
        }
        
        """
    return query


def create_set_statement_for_properties(
    node: EditNodeBase, node_identifier: str
) -> tuple[str, dict[str, Any]]:
    properties = node.base_class.property_fields

    set_query = """
    
    """
    set_params = {}
    for property_name, property in properties.items():
        # Don't update uid
        if property_name == "uid":
            continue

        value = getattr(node, property_name, None)
        if value:
            key_identifier = get_unique_string()
            set_params[key_identifier] = convert_type_for_writing(value)
            set_query += f"""SET {node_identifier}.{property_name} = ${key_identifier}
            """

    return set_query, set_params


def build_update_related_inline_editable_query(
    node, relation_name, start_node_identifier, delete_node_on_detach=False
) -> tuple[str, dict[str, Any]]:
    related_item_array_identifier = get_unique_string()

    related_items = getattr(node, relation_name, [])
    related_items_dict = [
        {key: convert_type_for_writing(value) for key, value in dict(item).items()}
        for item in related_items
    ]

    params = {related_item_array_identifier: related_items_dict}

    # print("----")
    # print("UPDATE", relation_name, "FOR", node)

    # print("RELATED_ITEMS", related_items)

    """
    SCENARIOS:
    
    - Inline node exists but not attached (attach; update?)
    - Inline node exists and is attached (update)
    - Inline node does not exist (create and attach)
    - Inline node is attached, but not in update (detach; maybe delete)
    
    """

    query = f"""
        CALL {{ // {relation_name} : Attach existing node if it is not attached
            WITH {start_node_identifier}
            UNWIND ${related_item_array_identifier} AS updated_related_item
                MATCH (node_to_relate {{uid: updated_related_item.uid}})
                WHERE NOT ({start_node_identifier})-[:{relation_name.upper()}]->(node_to_relate)
                CREATE ({start_node_identifier})-[:{relation_name.upper()}]->(node_to_relate)
        }}
        CALL {{ // {relation_name} : If not in list but is related, delete relation
            WITH {start_node_identifier}
            WITH {start_node_identifier}, [x IN ${related_item_array_identifier} | x.uid] AS updated_related_items_uids
            MATCH ({start_node_identifier})-[existing_rel_to_delete:{relation_name.upper()}]->(currently_related_item)
            WHERE NOT currently_related_item.uid IN updated_related_items_uids
            DELETE existing_rel_to_delete
            {"DELETE currently_related_item" if delete_node_on_detach else ""}
        }}
    """

    for related_node in related_items:
        related_node_parameter = get_unique_string()
        related_node_uid_parameter = get_unique_string()
        related_node_identifier = get_unique_string()
        # print(">>",related_node)
        update_query, update_params = build_update_node_query_and_params(
            related_node, related_node_identifier
        )

        params = {
            **params,
            **update_params,
            related_node_parameter: {
                key: convert_type_for_writing(value)
                for key, value in dict(related_node).items()
            },
            related_node_uid_parameter: str(related_node.uid),
        }
        query += f"""         
        CALL {{ // {relation_name}, {related_node} Exists and is attached; update
            WITH {start_node_identifier}
            MATCH ({related_node_identifier} {{uid: ${related_node_uid_parameter}}})
            WHERE ({start_node_identifier})-[:{relation_name.upper()}]->({related_node_identifier})
            
            {update_query}
                
        }}"""

        extra_labels = ["CreateInline", "ReadInline", "EditInline"]
        if node.outgoing_relations[
            relation_name
        ].relation_config.delete_related_on_detach:
            extra_labels.append("DeleteDetach")

        (
            related_node_identifier,
            query_match_clauses,
            query_create_clauses,
            query_params_dict,
        ) = build_write_query_and_params_dict(related_node, extra_labels=extra_labels)

        current_node_uid_identifier = get_unique_string()
        params = {
            **params,
            **query_params_dict,
            current_node_uid_identifier: str(node.uid),
        }

        query_params_string = (
            "{"
            + ", ".join(
                f"{key}: ${key}"
                for key, value in {
                    **query_params_dict,
                    current_node_uid_identifier: f"$current_node_uid_identifier",
                }.items()
            )
            + "}"
        )

        query += f"""
        CALL {{
            WITH {start_node_identifier}
            OPTIONAL MATCH (target {{uid: ${related_node_uid_parameter}}})
            CALL apoc.do.when(target IS NULL, '
                MATCH ({start_node_identifier} {{uid: ${current_node_uid_identifier}}})
                {"".join(query_match_clauses)}
                {"".join(query_create_clauses)}
                CREATE ({start_node_identifier})-[:{relation_name.upper()}]->({related_node_identifier})
            ', '', {query_params_string}) YIELD value
            RETURN value as {get_unique_string()}
            
        }}
        
        """

    return query, params


def build_update_related_query(node, relation_name, start_node_identifier):
    # print("SHOULD NOT BE CALLED")
    related_item_array_identifier = get_unique_string()

    params = {
        related_item_array_identifier: [
            {"uid": str(item.uid), "label": item.label, "real_type": item.real_type}
            for item in getattr(node, relation_name, [])
        ]
    }

    query = f"""
    CALL {{ // Attach existing node if it is not attached
        WITH {start_node_identifier}
        UNWIND ${related_item_array_identifier} AS updated_related_item
            MATCH (node_to_relate {{uid: updated_related_item.uid}})
            WHERE NOT ({start_node_identifier})-[:{relation_name.upper()}]->(node_to_relate)
            CREATE ({start_node_identifier})-[:{relation_name.upper()}]->(node_to_relate)
    }}
    CALL {{ // If not in list but is related, delete relation
        WITH {start_node_identifier}
        WITH {start_node_identifier}, [x IN ${related_item_array_identifier} | x.uid] AS updated_related_items_uids
        MATCH ({start_node_identifier})-[existing_rel_to_delete:{relation_name.upper()}]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN updated_related_items_uids
        DELETE existing_rel_to_delete
    }}
    
    """
    return query, params


def build_update_node_query_and_params(
    node, node_identifier
) -> tuple[str, dict[str, Any]]:
    # print("=======")
    # print("UPDATE NODE>", node)
    params = {}

    # Add in property updates for the node
    (
        set_properties_statements,
        set_properties_params,
    ) = create_set_statement_for_properties(node, node_identifier)
    params = {**params, **set_properties_params}

    # Add direct relations (non-updateable) for the node
    relations_subquery = """"""

    for relation_name, relation in node.base_class.outgoing_relations.items():
        # print("~", relation_name)
        if not relation.relation_config.edit_inline:
            values = getattr(node, relation_name)
            if values:
                related_query, related_params = build_update_related_query(
                    node, relation_name, node_identifier
                )
                relations_subquery += related_query
                params = {**params, **related_params}
        if relation.relation_config.edit_inline:
            values = getattr(node, relation_name)
            # print(values)
            if values:
                (
                    related_query,
                    related_params,
                ) = build_update_related_inline_editable_query(
                    node,
                    relation_name,
                    node_identifier,
                    delete_node_on_detach=relation.relation_config.delete_related_on_detach,
                )
                relations_subquery += related_query
                params = {**params, **related_params}

    query = f"""
    
    // Set relation queries
    {relations_subquery}
    
    // Set properties
    {set_properties_statements}
    
    """

    return query, params


def update_query(node: EditNodeBase) -> tuple[str, dict[str, Any]]:
    node_identifier = get_unique_string()
    node_uid_param = get_unique_string()

    params = {node_uid_param: str(node.uid)}
    query = f"""
    // Get the main node
    MATCH ({node_identifier} {{uid: ${node_uid_param}}})
    """

    node_query, node_params = build_update_node_query_and_params(node, node_identifier)

    params = {**params, **node_params}
    query += node_query

    with open("update_query.cypher", "w") as f:
        f.write(query)

    # (params)
    return query, params
