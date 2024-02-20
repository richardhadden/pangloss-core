
        MATCH (xa4fe4a {uid: $x759ddb})

        MATCH (xb89d01 {uid: $x22e588})
        CREATE (x5ef7e1:Event:BaseNode {uid: $x3cb1c0, label: $xc9338c, real_type: $x1bf7a7})

        CREATE (x5ef7e1)-[:WHEN {reverse_name: $x183564, relation_labels: $x401321}]->(xa4fe4a)

        CREATE (xb1c9e6:PersonIdentification:ReifiedRelation {uid: $x771773, identification_type: $x2350d8, real_type: $xab6df6})

        CREATE (xb1c9e6)-[:TARGET {reverse_name: $xa750b4, relation_labels: $xbf1f61, certainty: $x2cead2}]->(xb89d01)

        CREATE (x5ef7e1)-[:PERSON_IDENTIFIED {reverse_name: $x032361, relation_labels: $xced512}]->(xb1c9e6)
        
        
        return x5ef7e1{.uid, .label, .real_type}
        {'x3cb1c0': '40d49564-64ed-4be4-a950-4c6fd640f11d', 'xc9338c': 'Big Bash', 'x1bf7a7': 'event', 'x183564': 'is_day_of_event', 'x401321': [], 'x759ddb': '4f870d10-ea9a-487c-a5c2-8d897c0ccbf4', 'x771773': 'dd8fa368-cc35-4bcb-aaf2-2dc51775f987', 'x2350d8': 'visual', 'xab6df6': 'personidentification[test_write_abstract_reification.<locals>.person]', 'xa750b4': 'is_identified_in', 'xbf1f61': [], 'x2cead2': 1, 'x22e588': '5e486d1f-ec58-4f49-877d-cdf9133c7db1', 'x032361': 'is_identification_of_person_in_event', 'xced512': []}