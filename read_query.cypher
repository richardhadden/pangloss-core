
        
        MATCH path_to_node = (node:Event {uid: $uid})
        
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
         RETURN value 
        
        