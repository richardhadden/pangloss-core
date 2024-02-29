MATCH (x6cf722 {uid: $x29789d}) // Order, 8e475de4-e070-4e0a-b0c3-ebcecc915d80, Bertie Wooster orders Olive Branch to make a payment

        
        
        
        MERGE (x2549fd:Payment:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $xf76638}) // Payment, 0041e4dd-643a-480c-9365-2dac8ab8b0df, Olive Branch makes payment
        ON CREATE
       
            
    SET x2549fd = $xcb5ab2 // {'uid': '0041e4dd-643a-480c-9365-2dac8ab8b0df', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}
    
            
        ON MATCH
            
    SET x2549fd = $xcb5ab2 // {'uid': '0041e4dd-643a-480c-9365-2dac8ab8b0df', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}
    
        
        WITH x6cf722, x2549fd // <<
          
    // ('PaymentEdit', UUID('0041e4dd-643a-480c-9365-2dac8ab8b0df'), 'Olive Branch makes payment')
    CALL { // Attach existing node if it is not attached
        WITH x2549fd
        UNWIND $x2e8fe9 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x2549fd)-[:PAYMENT_MADE_BY]->(node_to_relate)
            CREATE (x2549fd)-[:PAYMENT_MADE_BY]->(node_to_relate)
    }
    // ('PaymentEdit', UUID('0041e4dd-643a-480c-9365-2dac8ab8b0df'), 'Olive Branch makes payment')
    CALL { // If not in list but is related, delete relation
        WITH x2549fd
        MATCH (x2549fd)-[existing_rel_to_delete:PAYMENT_MADE_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x2e8fe9
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x6cf722)-[:THING_ORDERED]->(x2549fd)
        

      WITH x6cf722, x2549fd // <<<<
        
    WITH x6cf722, x2549fd // <<<<
        
    CALL { // cleanup from Bertie Wooster orders Olive Branch to make a payment
       WITH x6cf722
       MATCH (x6cf722)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
       
        WHERE NOT currently_related_item.uid IN $xdf6331
        DELETE existing_rel_to_delete
        
        WITH currently_related_item
        CALL {
                       WITH currently_related_item
            MATCH delete_path = (currently_related_item:DeleteDetach)(()-->(:DeleteDetach)){0,}(:DeleteDetach) 
            UNWIND nodes(delete_path) as x
           DETACH DELETE x 
           
        }
           
           
        
        
        
    }
           
            
        
    // ('OrderEdit', UUID('8e475de4-e070-4e0a-b0c3-ebcecc915d80'), 'Bertie Wooster orders Olive Branch to make a payment')
    CALL { // Attach existing node if it is not attached
        WITH x6cf722
        UNWIND $xae1c18 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x6cf722)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (x6cf722)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('8e475de4-e070-4e0a-b0c3-ebcecc915d80'), 'Bertie Wooster orders Olive Branch to make a payment')
    CALL { // If not in list but is related, delete relation
        WITH x6cf722
        MATCH (x6cf722)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xae1c18
        DELETE existing_rel_to_delete
    }
    
    SET x6cf722 = $xbe1fbe // {'uid': '8e475de4-e070-4e0a-b0c3-ebcecc915d80', 'label': 'Bertie Wooster orders Olive Branch to make a payment', 'real_type': 'order'}
    



{'x29789d': '8e475de4-e070-4e0a-b0c3-ebcecc915d80', 'xbe1fbe': {'uid': '8e475de4-e070-4e0a-b0c3-ebcecc915d80', 'label': 'Bertie Wooster orders Olive Branch to make a payment', 'real_type': 'order'}, 'xdf6331': ['0041e4dd-643a-480c-9365-2dac8ab8b0df'], 'xf76638': '0041e4dd-643a-480c-9365-2dac8ab8b0df', 'xcb5ab2': {'uid': '0041e4dd-643a-480c-9365-2dac8ab8b0df', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}, 'x2e8fe9': ['e78b1c01-7c20-4f9d-b443-23f1f18fb16a'], 'xae1c18': ['8404491e-946e-4af7-bb56-6041fe7b7817']}