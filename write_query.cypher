
        MATCH (x6912d3 {uid: $xb56b51})

        MATCH (x77948b {uid: $x6af4f7})

        MATCH (xe4d307 {uid: $xe42378})
        CREATE (x71f33a:Person:BaseNode {uid: $xfe3fec, label: $xc0853d, real_type: $x96311f, created_when: datetime(), modified_when: datetime()})

        CREATE (xd05424:OuterTypeOne:BaseNode:Embedded:DeleteDetach {uid: $x7099b6, some_value: $xb65eb6, real_type: $x2f3d43, created_when: datetime(), modified_when: datetime()})

        CREATE (xb4c0d9:Inner:BaseNode:Embedded:DeleteDetach {uid: $xdca55a, name: $x32cf1a, real_type: $x20cc7f, created_when: datetime(), modified_when: datetime()})

        CREATE (xb4c0d9)-[:INNER_HAS_PET {reverse_name: $xb431d2, relation_labels: $x0c3c9e}]->(x6912d3)

        CREATE (xd05424)-[:INNER]->(xb4c0d9)

        CREATE (xd05424)-[:OUTER_ONE_HAS_PET {reverse_name: $x27be30, relation_labels: $xc6a17d}]->(x77948b)

        CREATE (x71f33a)-[:OUTER]->(xd05424)

        CREATE (x71f33a)-[:PERSON_HAS_PET {reverse_name: $x466dad, relation_labels: $xf525a3}]->(xe4d307)
        
        
        return x71f33a{.uid, .label, .real_type}
        {'xfe3fec': '799735dc-fa48-4839-9639-afab7f2b3d87', 'xc0853d': 'John Smith', 'x96311f': 'person', 'x7099b6': '51914526-f5fa-4216-b227-224aeb3b5359', 'xb65eb6': 'SomeValue', 'x2f3d43': 'outertypeone', 'xdca55a': '8875a3ca-296e-4bfc-bea9-7f93697ad1c5', 'x32cf1a': 'InnerEmbedded', 'x20cc7f': 'inner', 'xb431d2': 'is_pet_of', 'x0c3c9e': [], 'xb56b51': '7f3631aa-d5d1-412e-baf3-2ded7f6453c2', 'x27be30': 'is_pet_of', 'xc6a17d': [], 'x6af4f7': 'd74452b8-1106-4224-b264-6fa7b100ef0f', 'x466dad': 'is_pet_of', 'xf525a3': [], 'xe42378': 'fab70678-f233-4440-b363-4d056438b234'}