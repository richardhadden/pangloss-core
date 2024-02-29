MATCH (x8a4da1 {uid: $x04df6e}) // Order, 68ce78c9-046d-4279-9313-e612f9963c8c, Bertie Wooster orders Lucky Jim to order Miss Marple to write a book

        
        
        
        MERGE (x157b2a:Order:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $xf535e6}) // Order, 3cc4d105-f078-47d8-bdeb-2aedaf904373, Lucky Jim orders Miss Marple to write a book
        ON CREATE
       
            
    SET x157b2a = $x020f3a // {'uid': '3cc4d105-f078-47d8-bdeb-2aedaf904373', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}
    
            
        ON MATCH
            
    SET x157b2a = $x020f3a // {'uid': '3cc4d105-f078-47d8-bdeb-2aedaf904373', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}
    
        
        WITH x157b2a, x8a4da1 // <<
          

        
        
        
        MERGE (xea9d15:WritingBook:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $xc9498b}) // WritingBook, 37bc1fff-f573-420b-aee3-079d3e9548c2, Miss Marple writes book
        ON CREATE
       
            
    SET xea9d15 = $x076286 // {'uid': '37bc1fff-f573-420b-aee3-079d3e9548c2', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}
    
            
        ON MATCH
            
    SET xea9d15 = $x076286 // {'uid': '37bc1fff-f573-420b-aee3-079d3e9548c2', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}
    
        
        WITH x157b2a, xea9d15, x8a4da1 // <<
          
    // ('WritingBookEdit', UUID('37bc1fff-f573-420b-aee3-079d3e9548c2'), 'Miss Marple writes book')
    CALL { // Attach existing node if it is not attached
        WITH xea9d15
        UNWIND $x74b66b AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xea9d15)-[:WRITTEN_BY]->(node_to_relate)
            CREATE (xea9d15)-[:WRITTEN_BY]->(node_to_relate)
    }
    // ('WritingBookEdit', UUID('37bc1fff-f573-420b-aee3-079d3e9548c2'), 'Miss Marple writes book')
    CALL { // If not in list but is related, delete relation
        WITH xea9d15
        MATCH (xea9d15)-[existing_rel_to_delete:WRITTEN_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x74b66b
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x157b2a)-[:THING_ORDERED]->(xea9d15)
        

      WITH x157b2a, xea9d15, x8a4da1 // <<<<
        
    WITH x157b2a, xea9d15, x8a4da1 // <<<<
        
    CALL { // cleanup from Lucky Jim orders Miss Marple to write a book
       WITH x157b2a
       MATCH (x157b2a)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xc3a0c5
        DELETE existing_rel_to_delete
        DETACH DELETE currently_related_item
    }
    // ('OrderEdit', UUID('3cc4d105-f078-47d8-bdeb-2aedaf904373'), 'Lucky Jim orders Miss Marple to write a book')
    CALL { // Attach existing node if it is not attached
        WITH x157b2a
        UNWIND $xb3732e AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x157b2a)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (x157b2a)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('3cc4d105-f078-47d8-bdeb-2aedaf904373'), 'Lucky Jim orders Miss Marple to write a book')
    CALL { // If not in list but is related, delete relation
        WITH x157b2a
        MATCH (x157b2a)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xb3732e
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x8a4da1)-[:THING_ORDERED]->(x157b2a)
        

      WITH x157b2a, x8a4da1 // <<<<
        
    WITH x157b2a, x8a4da1 // <<<<
        
    CALL { // cleanup from Bertie Wooster orders Lucky Jim to order Miss Marple to write a book
       WITH x8a4da1
       MATCH (x8a4da1)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xd4eeeb
        DELETE existing_rel_to_delete
        DETACH DELETE currently_related_item
    }
    // ('OrderEdit', UUID('68ce78c9-046d-4279-9313-e612f9963c8c'), 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book')
    CALL { // Attach existing node if it is not attached
        WITH x8a4da1
        UNWIND $xd9d7d1 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x8a4da1)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (x8a4da1)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('68ce78c9-046d-4279-9313-e612f9963c8c'), 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book')
    CALL { // If not in list but is related, delete relation
        WITH x8a4da1
        MATCH (x8a4da1)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xd9d7d1
        DELETE existing_rel_to_delete
    }
    
    SET x8a4da1 = $x2a2d25 // {'uid': '68ce78c9-046d-4279-9313-e612f9963c8c', 'label': 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book', 'real_type': 'order'}
    



{'x04df6e': '68ce78c9-046d-4279-9313-e612f9963c8c', 'x2a2d25': {'uid': '68ce78c9-046d-4279-9313-e612f9963c8c', 'label': 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book', 'real_type': 'order'}, 'xd4eeeb': ['3cc4d105-f078-47d8-bdeb-2aedaf904373'], 'xf535e6': '3cc4d105-f078-47d8-bdeb-2aedaf904373', 'x020f3a': {'uid': '3cc4d105-f078-47d8-bdeb-2aedaf904373', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}, 'xc3a0c5': ['37bc1fff-f573-420b-aee3-079d3e9548c2'], 'xc9498b': '37bc1fff-f573-420b-aee3-079d3e9548c2', 'x076286': {'uid': '37bc1fff-f573-420b-aee3-079d3e9548c2', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}, 'x74b66b': ['ff193b1a-e50b-4656-82ab-d9c0d000cca1'], 'xb3732e': ['01a89a75-495d-4cfd-a91a-8db9773e27ca'], 'xd9d7d1': ['7810bd82-3ffe-44af-8c86-0f2e4f959289']}