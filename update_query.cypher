MATCH (x549f93 {uid: $xaa9a35}) // Person, 18a48591-c059-440f-9b05-a33b56753187, John Smith

        
        
        
        MERGE (xdf6b75:OuterTypeTwo:BaseNode:Embedded:DeleteDetach {uid: $x34bd72, real_type: $x81cbcc}) // OuterTypeTwo, 84687802-9f3d-4cae-9fa6-5ba19c701267
        ON CREATE
       
            
    SET xdf6b75 = $x9ebb7f // {'uid': '84687802-9f3d-4cae-9fa6-5ba19c701267', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
            
        ON MATCH
            
    SET xdf6b75 = $x9ebb7f // {'uid': '84687802-9f3d-4cae-9fa6-5ba19c701267', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}
    
        
        WITH x549f93, xdf6b75 // <<
          

        
        
        
        MERGE (xcad2a7:Inner:BaseNode:Embedded:DeleteDetach {uid: $xe4e997, real_type: $xf334bf}) // Inner, 322c97d8-34da-483b-b228-4409d4a98856
        ON CREATE
       
            
    SET xcad2a7 = $x71f408 // {'uid': '322c97d8-34da-483b-b228-4409d4a98856', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
            
        ON MATCH
            
    SET xcad2a7 = $x71f408 // {'uid': '322c97d8-34da-483b-b228-4409d4a98856', 'name': 'InnerEmbedded', 'real_type': 'inner'}
    
        
        WITH x549f93, xcad2a7, xdf6b75 // <<
          
    // ('InnerEmbedded', UUID('322c97d8-34da-483b-b228-4409d4a98856'))
    CALL { // Attach existing node if it is not attached
        WITH xcad2a7
        UNWIND $x7505a1 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xcad2a7)-[:INNER_HAS_PET]->(node_to_relate)
            CREATE (xcad2a7)-[:INNER_HAS_PET]->(node_to_relate)
    }
    // ('InnerEmbedded', UUID('322c97d8-34da-483b-b228-4409d4a98856'))
    CALL { // If not in list but is related, delete relation
        WITH xcad2a7
        MATCH (xcad2a7)-[existing_rel_to_delete:INNER_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x7505a1
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xdf6b75)-[:INNER]->(xcad2a7)
        

      WITH x549f93, xcad2a7, xdf6b75 // <<<<
        
    WITH x549f93, xcad2a7, xdf6b75 // <<<<
        
    CALL  {
       WITH xdf6b75
       MATCH (xdf6b75)-[existing_rel_to_delete:INNER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x0aa94e
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('OuterTypeTwoEmbedded', UUID('84687802-9f3d-4cae-9fa6-5ba19c701267'))
    CALL { // Attach existing node if it is not attached
        WITH xdf6b75
        UNWIND $x44a44b AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xdf6b75)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
            CREATE (xdf6b75)-[:OUTER_TWO_HAS_PET]->(node_to_relate)
    }
    // ('OuterTypeTwoEmbedded', UUID('84687802-9f3d-4cae-9fa6-5ba19c701267'))
    CALL { // If not in list but is related, delete relation
        WITH xdf6b75
        MATCH (xdf6b75)-[existing_rel_to_delete:OUTER_TWO_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x44a44b
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x549f93)-[:OUTER]->(xdf6b75)
        

      WITH x549f93, xdf6b75 // <<<<
        
    WITH x549f93, xdf6b75 // <<<<
        
    CALL  {
       WITH x549f93
       MATCH (x549f93)-[existing_rel_to_delete:OUTER]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $x563ff5
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
        
    }
    // ('PersonEdit', UUID('18a48591-c059-440f-9b05-a33b56753187'))
    CALL { // Attach existing node if it is not attached
        WITH x549f93
        UNWIND $x36585c AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x549f93)-[:PERSON_HAS_PET]->(node_to_relate)
            CREATE (x549f93)-[:PERSON_HAS_PET]->(node_to_relate)
    }
    // ('PersonEdit', UUID('18a48591-c059-440f-9b05-a33b56753187'))
    CALL { // If not in list but is related, delete relation
        WITH x549f93
        MATCH (x549f93)-[existing_rel_to_delete:PERSON_HAS_PET]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x36585c
        DELETE existing_rel_to_delete
    }
    
    SET x549f93 = $x1c2499 // {'uid': '18a48591-c059-440f-9b05-a33b56753187', 'label': 'John Smith', 'real_type': 'person'}
    RETURN x549f93{.uid}



{'xaa9a35': '18a48591-c059-440f-9b05-a33b56753187', 'x1c2499': {'uid': '18a48591-c059-440f-9b05-a33b56753187', 'label': 'John Smith', 'real_type': 'person'}, 'x563ff5': ['84687802-9f3d-4cae-9fa6-5ba19c701267'], 'x34bd72': '84687802-9f3d-4cae-9fa6-5ba19c701267', 'x81cbcc': 'outertypetwo', 'x9ebb7f': {'uid': '84687802-9f3d-4cae-9fa6-5ba19c701267', 'some_other_value': 'SomeValue', 'real_type': 'outertypetwo'}, 'x0aa94e': ['322c97d8-34da-483b-b228-4409d4a98856'], 'xe4e997': '322c97d8-34da-483b-b228-4409d4a98856', 'xf334bf': 'inner', 'x71f408': {'uid': '322c97d8-34da-483b-b228-4409d4a98856', 'name': 'InnerEmbedded', 'real_type': 'inner'}, 'x7505a1': ['446f9df4-dc0b-4cf3-a03f-9c6362c28b91'], 'x44a44b': ['0e334407-d463-40ed-8894-04af0d10ed71'], 'x36585c': ['671027e2-29a6-41bb-bb1d-0cd1a034d022']}