
        
        MATCH path_to_node = (node:Order {uid: $uid})
        
        CALL {
            WITH node, path_to_node
            OPTIONAL MATCH path_to_direct_nodes = (node)-[]->(:BaseNode)
            OPTIONAL MATCH path_through_read_nodes = (node)-[]->(:ReadInline)((:ReadInline)-[]->(:ReadInline)){0,}(:ReadInline)-[]->{0,}(:BaseNode)
            
            OPTIONAL MATCH path_to_reified = (node)-[]->(:ReifiedRelation)-[]->(:BaseNode)
            WITH apoc.coll.flatten([
                collect(path_to_direct_nodes),
                
                collect(path_through_read_nodes),
                collect(path_to_node),
                collect(path_to_reified)
            ]) AS paths, node
            CALL apoc.convert.toTree(paths)
            YIELD value
            RETURN value as value
        }
        WITH node, value
        CALL {
            WITH node
            CALL {
                WITH node
                OPTIONAL MATCH (node)<--(x WHERE (x:ReifiedRelation))(()<--()){ 0, }()<-[reverse_relation]-(related_node)
                WHERE NOT related_node:Embedded AND NOT related_node:ReifiedRelation
                WITH reverse_relation.reverse_name AS reverse_relation_type, collect(related_node{ .uid, .label, .real_type }) AS related_node_data
                RETURN collect({ t: reverse_relation_type, related_node_data: related_node_data }) AS via_reified
            }
            CALL {
                WITH node
                OPTIONAL MATCH (node)<-[reverse_relation]-(x WHERE (x:Embedded))(()<--()){ 0, }()<--(related_node)
                WHERE NOT related_node:Embedded AND NOT related_node:ReifiedRelation
                WITH reverse_relation.reverse_name AS reverse_relation_type, collect(related_node{ .uid, .label, .real_type }) AS related_node_data
                RETURN collect({ t: reverse_relation_type, related_node_data: related_node_data }) AS via_embedded
            }
            CALL {
                WITH node
                MATCH (node)<-[reverse_relation]-(related_node:BaseNode)
                WHERE NOT related_node:Embedded AND NOT related_node:ReifiedRelation
                WITH reverse_relation.reverse_name AS reverse_relation_type, collect(related_node{ .uid, .label, .real_type }) AS related_node_data
                RETURN collect({ t: reverse_relation_type, related_node_data: related_node_data }) AS direct_incoming
            }
            RETURN REDUCE(s = { }, item IN apoc.coll.flatten([direct_incoming, via_reified, via_embedded]) | apoc.map.setEntry(s, item.t, item.related_node_data)) AS reverse_relations
        }

        WITH value, node, reverse_relations
        RETURN apoc.map.mergeList([node, reverse_relations, value])
        
        