MATCH (x38fc8c {uid: $x2c50b8}) // Person, f34e8587-30eb-4c6f-8a0a-e42b3759eab1, John Smith

        
        
        
        MERGE (x461897:OuterTypeTwo:BaseNode:Embedded:DeleteDetach {uid: $x255eab, real_type: $x7aba82}) // OuterTypeTwo, 0522fbb8-3aac-4d89-9a82-2f807bcf869c
        ON CREATE
       
            
    SET x461897 = $x298860 // {'uid': '0522fbb8-3aac-4d89-9a82-2f807bcf869c', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913931), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913936), 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
            
        ON MATCH
            
    SET x461897 = $x298860 // {'uid': '0522fbb8-3aac-4d89-9a82-2f807bcf869c', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913931), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913936), 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
        
        WITH x461897, x38fc8c // <<
          

        
        
        
        MERGE (xcee23b:Inner:BaseNode:Embedded:DeleteDetach {uid: $x48e99b, real_type: $xb7f567}) // Inner, 2566c085-c544-4532-9ad3-cf8e433122da
        ON CREATE
       
            
    SET xcee23b = $xd5493e // {'uid': '2566c085-c544-4532-9ad3-cf8e433122da', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913945), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913947), 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
            
        ON MATCH
            
    SET xcee23b = $xd5493e // {'uid': '2566c085-c544-4532-9ad3-cf8e433122da', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913945), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913947), 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
        
        WITH x461897, x38fc8c, xcee23b // <<
          
    // ('InnerEmbedded', UUID('2566c085-c544-4532-9ad3-cf8e433122da'))
    CALL { // Attach existing node if it is not attached
        WITH xcee23b
        UNWIND $x348d6a AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xcee23b)-[:INNER_HAS_PET]->(node_to_relate)
            CREATE (xcee23b)-[:INNER_HAS_PET]->(node_to_relate)
    }
    // ('InnerEmbedded', UUID('2566c085-c544-4532-9ad3-cf8e433122da'))
    CALL { // If not in list but is related, delete relation
        WITH xcee23b
        MATCH (xcee23b)-[existing_rel_to_delete:INNER_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x348d6a
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x461897)-[:INNER]->(xcee23b)
        

      WITH x461897, x38fc8c, xcee23b // <<<<
        
    WITH x461897, x38fc8c, xcee23b // <<<<
        
    CALL  {
       WITH x461897
       MATCH (x461897)-[existing_rel_to_delete:INNER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x2360dd
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('OuterTypeTwoEmbedded', UUID('0522fbb8-3aac-4d89-9a82-2f807bcf869c'))
    CALL { // Attach existing node if it is not attached
        WITH x461897
        UNWIND $x463e61 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x461897)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
            CREATE (x461897)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
    }
    // ('OuterTypeTwoEmbedded', UUID('0522fbb8-3aac-4d89-9a82-2f807bcf869c'))
    CALL { // If not in list but is related, delete relation
        WITH x461897
        MATCH (x461897)-[existing_rel_to_delete:OUTER_TWO_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x463e61
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x38fc8c)-[:OUTER]->(x461897)
        

      WITH x461897, x38fc8c // <<<<
        
    WITH x461897, x38fc8c // <<<<
        
    CALL  {
       WITH x38fc8c
       MATCH (x38fc8c)-[existing_rel_to_delete:OUTER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $xa57c12
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('PersonEdit', UUID('f34e8587-30eb-4c6f-8a0a-e42b3759eab1'))
    CALL { // Attach existing node if it is not attached
        WITH x38fc8c
        UNWIND $xe2e7f5 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x38fc8c)-[:PERSON_HAS_PET]->(node_to_relate)
            CREATE (x38fc8c)-[:PERSON_HAS_PET]->(node_to_relate)
    }
    // ('PersonEdit', UUID('f34e8587-30eb-4c6f-8a0a-e42b3759eab1'))
    CALL { // If not in list but is related, delete relation
        WITH x38fc8c
        MATCH (x38fc8c)-[existing_rel_to_delete:PERSON_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xe2e7f5
        DELETE existing_rel_to_delete
    }
    
    SET x38fc8c = $x3837fa // {'uid': 'f34e8587-30eb-4c6f-8a0a-e42b3759eab1', 'label': 'John Smith', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913997), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913998), 'real_type': 'person'}
    RETURN x38fc8c{.uid}



{'x2c50b8': 'f34e8587-30eb-4c6f-8a0a-e42b3759eab1', 'x3837fa': {'uid': 'f34e8587-30eb-4c6f-8a0a-e42b3759eab1', 'label': 'John Smith', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913997), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913998), 'real_type': 'person'}, 'xa57c12': ['0522fbb8-3aac-4d89-9a82-2f807bcf869c'], 'x255eab': '0522fbb8-3aac-4d89-9a82-2f807bcf869c', 'x7aba82': 'outertypetwo', 'x298860': {'uid': '0522fbb8-3aac-4d89-9a82-2f807bcf869c', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913931), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913936), 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}, 'x2360dd': ['2566c085-c544-4532-9ad3-cf8e433122da'], 'x48e99b': '2566c085-c544-4532-9ad3-cf8e433122da', 'xb7f567': 'inner', 'xd5493e': {'uid': '2566c085-c544-4532-9ad3-cf8e433122da', 'created_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913945), 'modified_when': datetime.datetime(2024, 3, 5, 11, 59, 36, 913947), 'name': 'InnerEmbedded', 'real_type': 'inner'}, 'x348d6a': ['f38cadd9-8b40-4524-a685-17ceb005f111'], 'x463e61': ['83d1646d-d5b9-45f6-8155-0cc2f8d98af6'], 'xe2e7f5': ['22d3de1a-d371-4e70-bf4b-a83749229745']}