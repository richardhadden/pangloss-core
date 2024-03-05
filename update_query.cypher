MATCH (xe19f97 {uid: $x300ffb}) // Person, 80215763-ea74-462e-b4ce-649c24bd7127, John Smith

        
        
        
        MERGE (x2c2252:OuterTypeTwo:BaseNode:Embedded:DeleteDetach {uid: $xf9842b, real_type: $x4f4b37}) // OuterTypeTwo, 0b533575-7f09-4441-b934-6c9e22ca6eca
        ON CREATE
       
            
    SET x2c2252 = apoc.map.merge($xf8ea47, {created_when: coalesce(x2c2252.created_when, datetime()), modified_when: datetime()}) // {'uid': '0b533575-7f09-4441-b934-6c9e22ca6eca', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
            
        ON MATCH
            
    SET x2c2252 = apoc.map.merge($xf8ea47, {created_when: coalesce(x2c2252.created_when, datetime()), modified_when: datetime()}) // {'uid': '0b533575-7f09-4441-b934-6c9e22ca6eca', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
        
        WITH xe19f97, x2c2252 // <<
          

        
        
        
        MERGE (xd5d17e:Inner:BaseNode:Embedded:DeleteDetach {uid: $x3b44dc, real_type: $xb2899d}) // Inner, e1a90535-fdb5-4f5e-9732-82ecb01fd392
        ON CREATE
       
            
    SET xd5d17e = apoc.map.merge($xa1c101, {created_when: coalesce(xd5d17e.created_when, datetime()), modified_when: datetime()}) // {'uid': 'e1a90535-fdb5-4f5e-9732-82ecb01fd392', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
            
        ON MATCH
            
    SET xd5d17e = apoc.map.merge($xa1c101, {created_when: coalesce(xd5d17e.created_when, datetime()), modified_when: datetime()}) // {'uid': 'e1a90535-fdb5-4f5e-9732-82ecb01fd392', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
        
        WITH xd5d17e, xe19f97, x2c2252 // <<
          
    // ('InnerEmbedded', UUID('e1a90535-fdb5-4f5e-9732-82ecb01fd392'))
    CALL { // Attach existing node if it is not attached
        WITH xd5d17e
        UNWIND $x1099d3 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xd5d17e)-[:INNER_HAS_PET]->(node_to_relate)
            CREATE (xd5d17e)-[:INNER_HAS_PET]->(node_to_relate)
    }
    // ('InnerEmbedded', UUID('e1a90535-fdb5-4f5e-9732-82ecb01fd392'))
    CALL { // If not in list but is related, delete relation
        WITH xd5d17e
        MATCH (xd5d17e)-[existing_rel_to_delete:INNER_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x1099d3
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x2c2252)-[:INNER]->(xd5d17e)
        

      WITH xd5d17e, xe19f97, x2c2252 // <<<<
        
    WITH xd5d17e, xe19f97, x2c2252 // <<<<
        
    CALL  {
       WITH x2c2252
       MATCH (x2c2252)-[existing_rel_to_delete:INNER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x637b0a
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('OuterTypeTwoEmbedded', UUID('0b533575-7f09-4441-b934-6c9e22ca6eca'))
    CALL { // Attach existing node if it is not attached
        WITH x2c2252
        UNWIND $x9ba4f0 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x2c2252)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
            CREATE (x2c2252)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
    }
    // ('OuterTypeTwoEmbedded', UUID('0b533575-7f09-4441-b934-6c9e22ca6eca'))
    CALL { // If not in list but is related, delete relation
        WITH x2c2252
        MATCH (x2c2252)-[existing_rel_to_delete:OUTER_TWO_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x9ba4f0
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xe19f97)-[:OUTER]->(x2c2252)
        

      WITH xe19f97, x2c2252 // <<<<
        
    WITH xe19f97, x2c2252 // <<<<
        
    CALL  {
       WITH xe19f97
       MATCH (xe19f97)-[existing_rel_to_delete:OUTER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x27000c
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('PersonEdit', UUID('80215763-ea74-462e-b4ce-649c24bd7127'))
    CALL { // Attach existing node if it is not attached
        WITH xe19f97
        UNWIND $x7db799 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xe19f97)-[:PERSON_HAS_PET]->(node_to_relate)
            CREATE (xe19f97)-[:PERSON_HAS_PET]->(node_to_relate)
    }
    // ('PersonEdit', UUID('80215763-ea74-462e-b4ce-649c24bd7127'))
    CALL { // If not in list but is related, delete relation
        WITH xe19f97
        MATCH (xe19f97)-[existing_rel_to_delete:PERSON_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x7db799
        DELETE existing_rel_to_delete
    }
    
    SET xe19f97 = apoc.map.merge($x152d99, {created_when: coalesce(xe19f97.created_when, datetime()), modified_when: datetime()}) // {'uid': '80215763-ea74-462e-b4ce-649c24bd7127', 'label': 'John Smith', 'real_type': 'person'}
    RETURN xe19f97{.uid}



{'x300ffb': '80215763-ea74-462e-b4ce-649c24bd7127', 'x152d99': {'uid': '80215763-ea74-462e-b4ce-649c24bd7127', 'label': 'John Smith', 'real_type': 'person'}, 'x27000c': ['0b533575-7f09-4441-b934-6c9e22ca6eca'], 'xf9842b': '0b533575-7f09-4441-b934-6c9e22ca6eca', 'x4f4b37': 'outertypetwo', 'xf8ea47': {'uid': '0b533575-7f09-4441-b934-6c9e22ca6eca', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}, 'x637b0a': ['e1a90535-fdb5-4f5e-9732-82ecb01fd392'], 'x3b44dc': 'e1a90535-fdb5-4f5e-9732-82ecb01fd392', 'xb2899d': 'inner', 'xa1c101': {'uid': 'e1a90535-fdb5-4f5e-9732-82ecb01fd392', 'name': 'InnerEmbedded', 'real_type': 'inner'}, 'x1099d3': ['71408889-4daf-4c56-90f9-0c67cc2dcf11'], 'x9ba4f0': ['43c792e2-f27c-4b8a-acdc-96a17ea83278'], 'x7db799': ['697414be-862c-47e7-bf56-d2db4dfacd4f']}