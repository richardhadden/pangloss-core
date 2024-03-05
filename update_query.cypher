MATCH (x52be7f {uid: $xee5761}) // Person, 67aa22ae-88af-4638-b5fb-8c4305d19b86, John Smith

        
        
        
        MERGE (xfec7a3:OuterTypeTwo:BaseNode:Embedded:DeleteDetach {uid: $xf55593, real_type: $xa9b7e8}) // OuterTypeTwo, 365609c5-b89e-4f37-925e-d6a16e28e2a4
        ON CREATE
       
            
    SET xfec7a3 = apoc.map.merge($xbb5f3c, {created_when: coalesce(xfec7a3.created_when, datetime()), modified_when: datetime()}) // {'uid': '365609c5-b89e-4f37-925e-d6a16e28e2a4', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
            
        ON MATCH
            
    SET xfec7a3 = apoc.map.merge($xbb5f3c, {created_when: coalesce(xfec7a3.created_when, datetime()), modified_when: datetime()}) // {'uid': '365609c5-b89e-4f37-925e-d6a16e28e2a4', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
        
        WITH x52be7f, xfec7a3 // <<
          

        
        
        
        MERGE (x023488:Inner:BaseNode:Embedded:DeleteDetach {uid: $x32f2ce, real_type: $x46688a}) // Inner, 2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d
        ON CREATE
       
            
    SET x023488 = apoc.map.merge($x2f1921, {created_when: coalesce(x023488.created_when, datetime()), modified_when: datetime()}) // {'uid': '2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
            
        ON MATCH
            
    SET x023488 = apoc.map.merge($x2f1921, {created_when: coalesce(x023488.created_when, datetime()), modified_when: datetime()}) // {'uid': '2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
        
        WITH x52be7f, xfec7a3, x023488 // <<
          
    // ('InnerEmbedded', UUID('2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d'))
    CALL { // Attach existing node if it is not attached
        WITH x023488
        UNWIND $x46614b AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x023488)-[:INNER_HAS_PET]->(node_to_relate)
            CREATE (x023488)-[:INNER_HAS_PET]->(node_to_relate)
    }
    // ('InnerEmbedded', UUID('2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d'))
    CALL { // If not in list but is related, delete relation
        WITH x023488
        MATCH (x023488)-[existing_rel_to_delete:INNER_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x46614b
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xfec7a3)-[:INNER]->(x023488)
        

      WITH x52be7f, xfec7a3, x023488 // <<<<
        
    WITH x52be7f, xfec7a3, x023488 // <<<<
        
    CALL  {
       WITH xfec7a3
       MATCH (xfec7a3)-[existing_rel_to_delete:INNER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x366ec6
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('OuterTypeTwoEmbedded', UUID('365609c5-b89e-4f37-925e-d6a16e28e2a4'))
    CALL { // Attach existing node if it is not attached
        WITH xfec7a3
        UNWIND $x0beef7 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xfec7a3)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
            CREATE (xfec7a3)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
    }
    // ('OuterTypeTwoEmbedded', UUID('365609c5-b89e-4f37-925e-d6a16e28e2a4'))
    CALL { // If not in list but is related, delete relation
        WITH xfec7a3
        MATCH (xfec7a3)-[existing_rel_to_delete:OUTER_TWO_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x0beef7
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x52be7f)-[:OUTER]->(xfec7a3)
        

      WITH x52be7f, xfec7a3 // <<<<
        
    WITH x52be7f, xfec7a3 // <<<<
        
    CALL  {
       WITH x52be7f
       MATCH (x52be7f)-[existing_rel_to_delete:OUTER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x18c3d8
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('PersonEdit', UUID('67aa22ae-88af-4638-b5fb-8c4305d19b86'))
    CALL { // Attach existing node if it is not attached
        WITH x52be7f
        UNWIND $x3ab6a4 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x52be7f)-[:PERSON_HAS_PET]->(node_to_relate)
            CREATE (x52be7f)-[:PERSON_HAS_PET]->(node_to_relate)
    }
    // ('PersonEdit', UUID('67aa22ae-88af-4638-b5fb-8c4305d19b86'))
    CALL { // If not in list but is related, delete relation
        WITH x52be7f
        MATCH (x52be7f)-[existing_rel_to_delete:PERSON_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x3ab6a4
        DELETE existing_rel_to_delete
    }
    
    SET x52be7f = apoc.map.merge($x5b6cfd, {created_when: coalesce(x52be7f.created_when, datetime()), modified_when: datetime()}) // {'uid': '67aa22ae-88af-4638-b5fb-8c4305d19b86', 'label': 'John Smith', 'real_type': 'person'}
    RETURN x52be7f{.uid}



{'xee5761': '67aa22ae-88af-4638-b5fb-8c4305d19b86', 'x5b6cfd': {'uid': '67aa22ae-88af-4638-b5fb-8c4305d19b86', 'label': 'John Smith', 'real_type': 'person'}, 'x18c3d8': ['365609c5-b89e-4f37-925e-d6a16e28e2a4'], 'xf55593': '365609c5-b89e-4f37-925e-d6a16e28e2a4', 'xa9b7e8': 'outertypetwo', 'xbb5f3c': {'uid': '365609c5-b89e-4f37-925e-d6a16e28e2a4', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}, 'x366ec6': ['2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d'], 'x32f2ce': '2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d', 'x46688a': 'inner', 'x2f1921': {'uid': '2f4f5a52-139a-4d48-9699-f1ebd5a0ff9d', 'name': 'InnerEmbedded', 'real_type': 'inner'}, 'x46614b': ['1a6def8f-6919-4a43-8033-9eae82ceef21'], 'x0beef7': ['9126d3a3-bc0c-4a29-bd47-c2007068ab74'], 'x3ab6a4': ['7826f45d-3c09-456d-80c6-25c98f17fdcc']}