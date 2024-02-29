MATCH (xb69a85 {uid: $x3d4caf}) // Order, fd832a1b-38c3-4424-9df2-e48e2d856c0b, Bertie Wooster orders Toby Jones to order Olive Branch to make a payment

        
        
        
        MERGE (xe636f9:Order:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x757897}) // Order, 40a7e213-7e1f-4fd7-bfe7-040747b518ef, Lucky Jim orders Olive Branch to make a payment UPDATED
        ON CREATE
       
            
    SET xe636f9 = $xdc8f14 // {'uid': '40a7e213-7e1f-4fd7-bfe7-040747b518ef', 'label': 'Lucky Jim orders Olive Branch to make a payment UPDATED', 'real_type': 'order'}
    
            
        ON MATCH
            
    SET xe636f9 = $xdc8f14 // {'uid': '40a7e213-7e1f-4fd7-bfe7-040747b518ef', 'label': 'Lucky Jim orders Olive Branch to make a payment UPDATED', 'real_type': 'order'}
    
        
        WITH xe636f9, xb69a85 // <<
          

        
        
        
        MERGE (x4f7621:Payment:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x2d7dd2}) // Payment, 330266bd-e4e5-4ac0-90f5-d1e309c5a750, Olive Branch makes payment
        ON CREATE
       
            
    SET x4f7621 = $xb9917b // {'uid': '330266bd-e4e5-4ac0-90f5-d1e309c5a750', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}
    
            
        ON MATCH
            
    SET x4f7621 = $xb9917b // {'uid': '330266bd-e4e5-4ac0-90f5-d1e309c5a750', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}
    
        
        WITH xe636f9, x4f7621, xb69a85 // <<
          
    // ('PaymentEdit', UUID('330266bd-e4e5-4ac0-90f5-d1e309c5a750'), 'Olive Branch makes payment')
    CALL { // Attach existing node if it is not attached
        WITH x4f7621
        UNWIND $x02a41e AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x4f7621)-[:PAYMENT_MADE_BY]->(node_to_relate)
            CREATE (x4f7621)-[:PAYMENT_MADE_BY]->(node_to_relate)
    }
    // ('PaymentEdit', UUID('330266bd-e4e5-4ac0-90f5-d1e309c5a750'), 'Olive Branch makes payment')
    CALL { // If not in list but is related, delete relation
        WITH x4f7621
        MATCH (x4f7621)-[existing_rel_to_delete:PAYMENT_MADE_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x02a41e
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xe636f9)-[:THING_ORDERED]->(x4f7621)
        

      WITH xe636f9, x4f7621, xb69a85 // <<<<
        
    WITH xe636f9, x4f7621, xb69a85 // <<<<
        
    CALL { // cleanup from Lucky Jim orders Olive Branch to make a payment UPDATED
       WITH xe636f9
       MATCH (xe636f9)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xcf2407
        DELETE existing_rel_to_delete
    }
    // ('OrderEdit', UUID('40a7e213-7e1f-4fd7-bfe7-040747b518ef'), 'Lucky Jim orders Olive Branch to make a payment UPDATED')
    CALL { // Attach existing node if it is not attached
        WITH xe636f9
        UNWIND $xfffd1f AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xe636f9)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (xe636f9)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('40a7e213-7e1f-4fd7-bfe7-040747b518ef'), 'Lucky Jim orders Olive Branch to make a payment UPDATED')
    CALL { // If not in list but is related, delete relation
        WITH xe636f9
        MATCH (xe636f9)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xfffd1f
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xb69a85)-[:THING_ORDERED]->(xe636f9)
        

      WITH xe636f9, xb69a85 // <<<<
        
    WITH xe636f9, xb69a85 // <<<<
        
    CALL { // cleanup from Bertie Wooster orders Toby Jones to order Olive Branch to make a payment
       WITH xb69a85
       MATCH (xb69a85)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x7aa103
        DELETE existing_rel_to_delete
    }
    // ('OrderEdit', UUID('fd832a1b-38c3-4424-9df2-e48e2d856c0b'), 'Bertie Wooster orders Toby Jones to order Olive Branch to make a payment')
    CALL { // Attach existing node if it is not attached
        WITH xb69a85
        UNWIND $x5cf505 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xb69a85)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (xb69a85)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('fd832a1b-38c3-4424-9df2-e48e2d856c0b'), 'Bertie Wooster orders Toby Jones to order Olive Branch to make a payment')
    CALL { // If not in list but is related, delete relation
        WITH xb69a85
        MATCH (xb69a85)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x5cf505
        DELETE existing_rel_to_delete
    }
    
    SET xb69a85 = $xc23fb6 // {'uid': 'fd832a1b-38c3-4424-9df2-e48e2d856c0b', 'label': 'Bertie Wooster orders Toby Jones to order Olive Branch to make a payment', 'real_type': 'order'}
    



{'x3d4caf': 'fd832a1b-38c3-4424-9df2-e48e2d856c0b', 'xc23fb6': {'uid': 'fd832a1b-38c3-4424-9df2-e48e2d856c0b', 'label': 'Bertie Wooster orders Toby Jones to order Olive Branch to make a payment', 'real_type': 'order'}, 'x7aa103': ['40a7e213-7e1f-4fd7-bfe7-040747b518ef'], 'x757897': '40a7e213-7e1f-4fd7-bfe7-040747b518ef', 'xdc8f14': {'uid': '40a7e213-7e1f-4fd7-bfe7-040747b518ef', 'label': 'Lucky Jim orders Olive Branch to make a payment UPDATED', 'real_type': 'order'}, 'xcf2407': ['330266bd-e4e5-4ac0-90f5-d1e309c5a750'], 'x2d7dd2': '330266bd-e4e5-4ac0-90f5-d1e309c5a750', 'xb9917b': {'uid': '330266bd-e4e5-4ac0-90f5-d1e309c5a750', 'label': 'Olive Branch makes payment', 'how_much': 1, 'real_type': 'payment'}, 'x02a41e': ['a3f1b7c7-48e1-4adc-ac96-d229eab5e016'], 'xfffd1f': ['d969f47b-9ba4-445a-ac2c-7effc164abd0'], 'x5cf505': ['50083235-6d0d-4250-bf11-322e2900fbc2']}