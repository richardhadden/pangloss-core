MATCH (xde98e8 {uid: $x6ec5de}) // Order, 80913483-1fac-414d-b2aa-28b204b52366, Bertie Wooster orders Lucky Jim to order Miss Marple to write a book

        
        
        
        MERGE (x6529de:Order:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $xbd3bad}) // Order, c694975a-07f4-4b3c-bcd2-1e725760d3d0, Lucky Jim orders Miss Marple to write a book
        ON CREATE
       
            
    SET x6529de = $xddf2b8 // {'uid': 'c694975a-07f4-4b3c-bcd2-1e725760d3d0', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}
    
            
        ON MATCH
            
    SET x6529de = $xddf2b8 // {'uid': 'c694975a-07f4-4b3c-bcd2-1e725760d3d0', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}
    
        
        WITH x6529de, xde98e8 // <<
          

        
        
        
        MERGE (x772920:WritingBook:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x4ed036}) // WritingBook, 5961ea0d-6b92-46c3-abb4-84cb6aa72b8e, Miss Marple writes book
        ON CREATE
       
            
    SET x772920 = $x4b6447 // {'uid': '5961ea0d-6b92-46c3-abb4-84cb6aa72b8e', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}
    
            
        ON MATCH
            
    SET x772920 = $x4b6447 // {'uid': '5961ea0d-6b92-46c3-abb4-84cb6aa72b8e', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}
    
        
        WITH x6529de, x772920, xde98e8 // <<
          
    // ('WritingBookEdit', UUID('5961ea0d-6b92-46c3-abb4-84cb6aa72b8e'), 'Miss Marple writes book')
    CALL { // Attach existing node if it is not attached
        WITH x772920
        UNWIND $xe06675 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x772920)-[:WRITTEN_BY]->(node_to_relate)
            CREATE (x772920)-[:WRITTEN_BY]->(node_to_relate)
    }
    // ('WritingBookEdit', UUID('5961ea0d-6b92-46c3-abb4-84cb6aa72b8e'), 'Miss Marple writes book')
    CALL { // If not in list but is related, delete relation
        WITH x772920
        MATCH (x772920)-[existing_rel_to_delete:WRITTEN_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xe06675
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (x6529de)-[:THING_ORDERED]->(x772920)
        

      WITH x6529de, x772920, xde98e8 // <<<<
        
    WITH x6529de, x772920, xde98e8 // <<<<
        
    CALL { // cleanup from Lucky Jim orders Miss Marple to write a book
       WITH x6529de
       MATCH (x6529de)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x0c785b
        DELETE existing_rel_to_delete
    }
    // ('OrderEdit', UUID('c694975a-07f4-4b3c-bcd2-1e725760d3d0'), 'Lucky Jim orders Miss Marple to write a book')
    CALL { // Attach existing node if it is not attached
        WITH x6529de
        UNWIND $x890768 AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (x6529de)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (x6529de)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('c694975a-07f4-4b3c-bcd2-1e725760d3d0'), 'Lucky Jim orders Miss Marple to write a book')
    CALL { // If not in list but is related, delete relation
        WITH x6529de
        MATCH (x6529de)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x890768
        DELETE existing_rel_to_delete
    }
    
        
        
        
        MERGE (xde98e8)-[:THING_ORDERED]->(x6529de)
        

      WITH x6529de, xde98e8 // <<<<
        
    WITH x6529de, xde98e8 // <<<<
        
    CALL { // cleanup from Bertie Wooster orders Lucky Jim to order Miss Marple to write a book
       WITH xde98e8
       MATCH (xde98e8)-[existing_rel_to_delete:THING_ORDERED]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $xb5c109
        DELETE existing_rel_to_delete
    }
    // ('OrderEdit', UUID('80913483-1fac-414d-b2aa-28b204b52366'), 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book')
    CALL { // Attach existing node if it is not attached
        WITH xde98e8
        UNWIND $x6036fb AS updated_related_item_uid
            MATCH (node_to_relate {uid: updated_related_item_uid})
            WHERE NOT (xde98e8)-[:CARRIED_OUT_BY]->(node_to_relate)
            CREATE (xde98e8)-[:CARRIED_OUT_BY]->(node_to_relate)
    }
    // ('OrderEdit', UUID('80913483-1fac-414d-b2aa-28b204b52366'), 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book')
    CALL { // If not in list but is related, delete relation
        WITH xde98e8
        MATCH (xde98e8)-[existing_rel_to_delete:CARRIED_OUT_BY]->(currently_related_item)
        WHERE NOT currently_related_item.uid IN $x6036fb
        DELETE existing_rel_to_delete
    }
    
    SET xde98e8 = $xe2f6c5 // {'uid': '80913483-1fac-414d-b2aa-28b204b52366', 'label': 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book', 'real_type': 'order'}
    



{'x6ec5de': '80913483-1fac-414d-b2aa-28b204b52366', 'xe2f6c5': {'uid': '80913483-1fac-414d-b2aa-28b204b52366', 'label': 'Bertie Wooster orders Lucky Jim to order Miss Marple to write a book', 'real_type': 'order'}, 'xb5c109': ['c694975a-07f4-4b3c-bcd2-1e725760d3d0'], 'xbd3bad': 'c694975a-07f4-4b3c-bcd2-1e725760d3d0', 'xddf2b8': {'uid': 'c694975a-07f4-4b3c-bcd2-1e725760d3d0', 'label': 'Lucky Jim orders Miss Marple to write a book', 'real_type': 'order'}, 'x0c785b': ['5961ea0d-6b92-46c3-abb4-84cb6aa72b8e'], 'x4ed036': '5961ea0d-6b92-46c3-abb4-84cb6aa72b8e', 'x4b6447': {'uid': '5961ea0d-6b92-46c3-abb4-84cb6aa72b8e', 'label': 'Miss Marple writes book', 'something': '', 'real_type': 'writingbook'}, 'xe06675': ['3ec1b9db-c3a4-49d1-b351-945cde25c0b2'], 'x890768': ['37b7665a-15af-41f2-8ca3-8592d292eeae'], 'x6036fb': ['b573cbaf-e093-4a9e-a56d-08b3931f74bb']}