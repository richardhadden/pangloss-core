MATCH (xe5e04b {uid: $x2b1aa7}) // Person, 7b7dc9d9-e480-4f29-a90c-14277c9becd8, John Smith

        
        
        
        MERGE (x4d1a10:OuterTypeTwo:BaseNode:Embedded:DeleteDetach {uid: $x3c154d, real_type: $x0f6fce}) // OuterTypeTwo, 7c2e55ff-1b4a-46af-8bba-2394a3487295
        ON CREATE
       
            
    SET x4d1a10 = apoc.map.merge($x8a17ef, {created_when: coalesce(x4d1a10.created_when, datetime()), modified_when: datetime()}) // {'uid': '7c2e55ff-1b4a-46af-8bba-2394a3487295', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
            
        ON MATCH
            
    SET x4d1a10 = apoc.map.merge($x8a17ef, {created_when: coalesce(x4d1a10.created_when, datetime()), modified_when: datetime()}) // {'uid': '7c2e55ff-1b4a-46af-8bba-2394a3487295', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
        
        WITH x4d1a10, xe5e04b // <<
          

        
        
        
        MERGE (x80fdec:Inner:BaseNode:Embedded:DeleteDetach {uid: $x77c762, real_type: $xc83c0a}) // Inner, 5863b2eb-3b93-492a-ab41-da13f9686285
        ON CREATE
       
            
    SET x80fdec = apoc.map.merge($xea6925, {created_when: coalesce(x80fdec.created_when, datetime()), modified_when: datetime()}) // {'uid': '5863b2eb-3b93-492a-ab41-da13f9686285', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
            
        ON MATCH
            
    SET x80fdec = apoc.map.merge($xea6925, {created_when: coalesce(x80fdec.created_when, datetime()), modified_when: datetime()}) // {'uid': '5863b2eb-3b93-492a-ab41-da13f9686285', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
        
        WITH x4d1a10, xe5e04b, x80fdec // <<
          
    // ('InnerEmbedded', UUID('5863b2eb-3b93-492a-ab41-da13f9686285'))
    CALL { // Attach existing node if it is not attached
        WITH x80fdec
        UNWIND $x69f6b8 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x80fdec)-[:INNER_HAS_PET]->(node_to_relate)
            CREATE (x80fdec)-[:INNER_HAS_PET]->(node_to_relate)
    }
    // ('InnerEmbedded', UUID('5863b2eb-3b93-492a-ab41-da13f9686285'))
    CALL { // If not in list but is related, delete relation
        WITH x80fdec
        MATCH (x80fdec)-[existing_rel_to_delete:INNER_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x69f6b8
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x4d1a10)-[:INNER]->(x80fdec)
        

      WITH x4d1a10, xe5e04b, x80fdec // <<<<
        
    WITH x4d1a10, xe5e04b, x80fdec // <<<<
        
    CALL  {
       WITH x4d1a10
       MATCH (x4d1a10)-[existing_rel_to_delete:INNER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x7963c9
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('OuterTypeTwoEmbedded', UUID('7c2e55ff-1b4a-46af-8bba-2394a3487295'))
    CALL { // Attach existing node if it is not attached
        WITH x4d1a10
        UNWIND $x907920 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x4d1a10)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
            CREATE (x4d1a10)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
    }
    // ('OuterTypeTwoEmbedded', UUID('7c2e55ff-1b4a-46af-8bba-2394a3487295'))
    CALL { // If not in list but is related, delete relation
        WITH x4d1a10
        MATCH (x4d1a10)-[existing_rel_to_delete:OUTER_TWO_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x907920
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xe5e04b)-[:OUTER]->(x4d1a10)
        

      WITH x4d1a10, xe5e04b // <<<<
        
    WITH x4d1a10, xe5e04b // <<<<
        
    CALL  {
       WITH xe5e04b
       MATCH (xe5e04b)-[existing_rel_to_delete:OUTER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x1d62ac
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('PersonEdit', UUID('7b7dc9d9-e480-4f29-a90c-14277c9becd8'))
    CALL { // Attach existing node if it is not attached
        WITH xe5e04b
        UNWIND $x065540 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xe5e04b)-[:PERSON_HAS_PET]->(node_to_relate)
            CREATE (xe5e04b)-[:PERSON_HAS_PET]->(node_to_relate)
    }
    // ('PersonEdit', UUID('7b7dc9d9-e480-4f29-a90c-14277c9becd8'))
    CALL { // If not in list but is related, delete relation
        WITH xe5e04b
        MATCH (xe5e04b)-[existing_rel_to_delete:PERSON_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x065540
        DELETE existing_rel_to_delete
    }
    
    SET xe5e04b = apoc.map.merge($x590af2, {created_when: coalesce(xe5e04b.created_when, datetime()), modified_when: datetime()}) // {'uid': '7b7dc9d9-e480-4f29-a90c-14277c9becd8', 'label': 'John Smith', 'real_type': 'person'}
    RETURN xe5e04b{.uid}



{'x2b1aa7': '7b7dc9d9-e480-4f29-a90c-14277c9becd8', 'x590af2': {'uid': '7b7dc9d9-e480-4f29-a90c-14277c9becd8', 'label': 'John Smith', 'real_type': 'person'}, 'x1d62ac': ['7c2e55ff-1b4a-46af-8bba-2394a3487295'], 'x3c154d': '7c2e55ff-1b4a-46af-8bba-2394a3487295', 'x0f6fce': 'outertypetwo', 'x8a17ef': {'uid': '7c2e55ff-1b4a-46af-8bba-2394a3487295', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}, 'x7963c9': ['5863b2eb-3b93-492a-ab41-da13f9686285'], 'x77c762': '5863b2eb-3b93-492a-ab41-da13f9686285', 'xc83c0a': 'inner', 'xea6925': {'uid': '5863b2eb-3b93-492a-ab41-da13f9686285', 'name': 'InnerEmbedded', 'real_type': 'inner'}, 'x69f6b8': ['7f3631aa-d5d1-412e-baf3-2ded7f6453c2'], 'x907920': ['536f7817-cd35-4507-8485-9e55edd5209e'], 'x065540': ['fab70678-f233-4440-b363-4d056438b234']}