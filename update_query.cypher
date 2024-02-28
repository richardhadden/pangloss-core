
    // Get the main node
    MATCH (xe782f4 {uid: $x887a10})
    
    
    // Set relation queries
    
        CALL { // thing_ordered : Attach existing node if it is not attached
            WITH xe782f4
            UNWIND $x5a06b8 AS updated_related_item
                MATCH (node_to_relate {uid: updated_related_item.uid})
                WHERE NOT (xe782f4)-[:THING_ORDERED]->(node_to_relate)
                CREATE (xe782f4)-[:THING_ORDERED]->(node_to_relate)
        }
        CALL { // thing_ordered : If not in list but is related, delete relation
            WITH xe782f4
            WITH xe782f4, [x IN $x5a06b8 | x.uid] AS updated_related_items_uids
            MATCH (xe782f4)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
            WHERE NOT currently_related_item.uid IN updated_related_items_uids
            DELETE existing_rel_to_delete
            DELETE currently_related_item
        }
             
        CALL { // thing_ordered, thing_ordered=[PaymentEdit(payment_made_by=[PersonReference(uid=UUID('fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3'), label='Olive Branch', real_type='person')], uid=UUID('7bac351f-e409-4ab1-9d7a-39a5a6dcb74a'), label='Olive Branch makes payment', how_much=1)] carried_out_by=[PersonReference(uid=UUID('113b5d69-c2fc-455c-8a54-c4f422af041d'), label='Toby Jones', real_type='person')] uid=UUID('de4f0fcd-54cf-474a-b2d6-2ec847826f13') label='Toby Jones orders Olive Branch to make a payment' Exists and is attached; update
            WITH xe782f4
            MATCH (xe189fd {uid: $x02cfb8})
            WHERE (xe782f4)-[:THING_ORDERED]->(xe189fd)
            
            
    
    // Set relation queries
    
        CALL { // thing_ordered : Attach existing node if it is not attached
            WITH xe189fd
            UNWIND $x250e5a AS updated_related_item
                MATCH (node_to_relate {uid: updated_related_item.uid})
                WHERE NOT (xe189fd)-[:THING_ORDERED]->(node_to_relate)
                CREATE (xe189fd)-[:THING_ORDERED]->(node_to_relate)
        }
        CALL { // thing_ordered : If not in list but is related, delete relation
            WITH xe189fd
            WITH xe189fd, [x IN $x250e5a | x.uid] AS updated_related_items_uids
            MATCH (xe189fd)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
            WHERE NOT currently_related_item.uid IN updated_related_items_uids
            DELETE existing_rel_to_delete
            DELETE currently_related_item
        }
             
        CALL { // thing_ordered, payment_made_by=[PersonReference(uid=UUID('fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3'), label='Olive Branch', real_type='person')] uid=UUID('7bac351f-e409-4ab1-9d7a-39a5a6dcb74a') label='Olive Branch makes payment' how_much=1 Exists and is attached; update
            WITH xe189fd
            MATCH (x42762d {uid: $x4cbfc8})
            WHERE (xe189fd)-[:THING_ORDERED]->(x42762d)
            
            
    
    // Set relation queries
    
    CALL { // Attach existing node if it is not attached
        WITH x42762d
        UNWIND $x08e270 AS updated_related_item
            MATCH (node_to_relate {uid: updated_related_item.uid})
            WHERE NOT (x42762d)-[:PAYMENT_MADE_BY]->(node_to_relate)
            CREATE (x42762d)-[:PAYMENT_MADE_BY]->(node_to_relate)
    }
    CALL { // If not in list but is related, delete relation
        WITH x42762d
        WITH x42762d, [x IN $x08e270 | x.uid] AS updated_related_items_uids
        MATCH (x42762d)-[existing_rel_to_delete:PAYMENT_MADE_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN updated_related_items_uids
        DELETE existing_rel_to_delete
    }
    
    
    
    // Set properties
    
    
    SET x42762d.label = $x2f2515
            SET x42762d.how_much = $x4d0008
            
    
    
                
        }
        CALL {
            WITH xe189fd
            OPTIONAL MATCH (target {uid: $x4cbfc8})
            CALL apoc.do.when(target IS NULL, '
                MATCH (xe189fd {uid: $xf7dc0b})
                MATCH (x229b8e {uid: $x1ba4ba})
                CREATE (xcdbf54:Payment:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x89adb5, label: $x2b78a8, how_much: $xce509f, real_type: $x5bf0b0})CREATE (xcdbf54)-[:PAYMENT_MADE_BY {reverse_name: $xab5218, relation_labels: $x856d8c}]->(x229b8e)
                CREATE (xe189fd)-[:THING_ORDERED]->(xcdbf54)
            ', '', {x89adb5: $x89adb5, x2b78a8: $x2b78a8, xce509f: $xce509f, x5bf0b0: $x5bf0b0, xab5218: $xab5218, x856d8c: $x856d8c, x1ba4ba: $x1ba4ba, xf7dc0b: $xf7dc0b}) YIELD value
            RETURN value as x48674b
            
        }
        
        
    CALL { // Attach existing node if it is not attached
        WITH xe189fd
        UNWIND $xae95e7 AS updated_related_item
            MATCH (node_to_relate {uid: updated_related_item.uid})
            WHERE NOT (xe189fd)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (xe189fd)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    CALL { // If not in list but is related, delete relation
        WITH xe189fd
        WITH xe189fd, [x IN $xae95e7 | x.uid] AS updated_related_items_uids
        MATCH (xe189fd)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN updated_related_items_uids
        DELETE existing_rel_to_delete
    }
    
    
    
    // Set properties
    
    
    SET xe189fd.label = $xa4de15
            
    
    
                
        }
        CALL {
            WITH xe782f4
            OPTIONAL MATCH (target {uid: $x02cfb8})
            CALL apoc.do.when(target IS NULL, '
                MATCH (xe782f4 {uid: $x645b66})
                MATCH (x64356e {uid: $x3eab74})MATCH (x530162 {uid: $x490ba8})
                CREATE (x35941f:Order:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x7d5055, label: $x1f9fd8, real_type: $x7b2178})CREATE (x963c1d:Payment:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $xcc7baa, label: $xf00090, how_much: $x10fb21, real_type: $x72dfb0})CREATE (x963c1d)-[:PAYMENT_MADE_BY {reverse_name: $x805366, relation_labels: $xdf5f36}]->(x64356e)CREATE (x35941f)-[:THING_ORDERED]->(x963c1d)CREATE (x35941f)-[:CARRIED_OUT_BY {reverse_name: $x067f73, relation_labels: $xfb7569}]->(x530162)
                CREATE (xe782f4)-[:THING_ORDERED]->(x35941f)
            ', '', {x7d5055: $x7d5055, x1f9fd8: $x1f9fd8, x7b2178: $x7b2178, xcc7baa: $xcc7baa, xf00090: $xf00090, x10fb21: $x10fb21, x72dfb0: $x72dfb0, x805366: $x805366, xdf5f36: $xdf5f36, x3eab74: $x3eab74, x067f73: $x067f73, xfb7569: $xfb7569, x490ba8: $x490ba8, x645b66: $x645b66}) YIELD value
            RETURN value as xd03009
            
        }
        
        
    CALL { // Attach existing node if it is not attached
        WITH xe782f4
        UNWIND $x855626 AS updated_related_item
            MATCH (node_to_relate {uid: updated_related_item.uid})
            WHERE NOT (xe782f4)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (xe782f4)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    CALL { // If not in list but is related, delete relation
        WITH xe782f4
        WITH xe782f4, [x IN $x855626 | x.uid] AS updated_related_items_uids
        MATCH (xe782f4)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN updated_related_items_uids
        DELETE existing_rel_to_delete
    }
    
    
    
    // Set properties
    
    
    SET xe782f4.label = $xec6d6f
            
    
    



{'x887a10': '625876b9-9bc8-4df6-ad2e-737cbeb206b8', 'xec6d6f': 'John Smith orders Toby Jones to order Olive Branch to make a payment', 'x5a06b8': [{'uid': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13'}], 'xa4de15': 'Toby Jones orders Olive Branch to make a payment', 'x250e5a': [{'uid': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a'}], 'x2f2515': 'Olive Branch makes payment', 'x4d0008': 1, 'x08e270': [{'uid': 'fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3', 'label': 'Olive Branch', 'real_type': 'person'}], 'x96a656': {'payment_made_by': [PersonReference(uid=UUID('fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3'), label='Olive Branch', real_type='person')], 'uid': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a', 'label': 'Olive Branch makes payment', 'how_much': 1}, 'x4cbfc8': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a', 'x89adb5': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a', 'x2b78a8': 'Olive Branch makes payment', 'xce509f': 1, 'x5bf0b0': 'payment', 'xab5218': 'made_payment', 'x856d8c': [], 'x1ba4ba': 'fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3', 'xf7dc0b': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13', 'xae95e7': [{'uid': '113b5d69-c2fc-455c-8a54-c4f422af041d', 'label': 'Toby Jones', 'real_type': 'person'}], 'xe2a6e7': {'thing_ordered': [PaymentEdit(payment_made_by=[PersonReference(uid=UUID('fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3'), label='Olive Branch', real_type='person')], uid=UUID('7bac351f-e409-4ab1-9d7a-39a5a6dcb74a'), label='Olive Branch makes payment', how_much=1)], 'carried_out_by': [PersonReference(uid=UUID('113b5d69-c2fc-455c-8a54-c4f422af041d'), label='Toby Jones', real_type='person')], 'uid': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13', 'label': 'Toby Jones orders Olive Branch to make a payment'}, 'x02cfb8': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13', 'x7d5055': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13', 'x1f9fd8': 'Toby Jones orders Olive Branch to make a payment', 'x7b2178': 'order', 'xcc7baa': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a', 'xf00090': 'Olive Branch makes payment', 'x10fb21': 1, 'x72dfb0': 'payment', 'x805366': 'made_payment', 'xdf5f36': [], 'x3eab74': 'fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3', 'x067f73': 'carried_out_order', 'xfb7569': [], 'x490ba8': '113b5d69-c2fc-455c-8a54-c4f422af041d', 'x645b66': '625876b9-9bc8-4df6-ad2e-737cbeb206b8', 'x855626': [{'uid': '54427fd0-ba1c-499a-9187-631a94eecd7a', 'label': 'John Smith', 'real_type': 'person'}]}