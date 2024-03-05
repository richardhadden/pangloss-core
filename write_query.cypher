
        MATCH (x0abced {uid: $xd0967c})

        MATCH (xe268e4 {uid: $xe4e115})

        MATCH (x36e789 {uid: $x92abf5})
        CREATE (xbf73dd:Person:BaseNode {uid: $xb7bb5e, label: $x2927c1, created_when: $x195304, modified_when: $x3b2f25, real_type: $x006466})

        CREATE (x9e35ee:OuterTypeOne:BaseNode:Embedded:DeleteDetach {uid: $x3de99a, created_when: $x05c39c, modified_when: $xb4a675, some_value: $x3736ea, real_type: $x9110a0})

        CREATE (x1ca976:Inner:BaseNode:Embedded:DeleteDetach {uid: $xb51d82, created_when: $x271a58, modified_when: $x9ee2aa, name: $x1cec64, real_type: $x7bf7f4})

        CREATE (x1ca976)-[:INNER_HAS_PET {reverse_name: $x076ad6, relation_labels: $x584e0c}]->(x0abced)

        CREATE (x9e35ee)-[:INNER]->(x1ca976)

        CREATE (x9e35ee)-[:OUTER_ONE_HAS_PET {reverse_name: $x66b61e, relation_labels: $xf5a073}]->(xe268e4)

        CREATE (xbf73dd)-[:OUTER]->(x9e35ee)

        CREATE (xbf73dd)-[:PERSON_HAS_PET {reverse_name: $x5b4eb0, relation_labels: $x6f28ef}]->(x36e789)
        
        
        return xbf73dd{.uid, .label, .real_type}
        {'xb7bb5e': '4c8e917b-5dc3-43c9-89ed-b3dac8143dc8', 'x2927c1': 'John Smith', 'x195304': datetime.datetime(2024, 3, 5, 11, 59, 36, 848120), 'x3b2f25': datetime.datetime(2024, 3, 5, 11, 59, 36, 848125), 'x006466': 'person', 'x3de99a': 'acfe359b-85e0-4841-a4c4-e57ce31a2e67', 'x05c39c': datetime.datetime(2024, 3, 5, 11, 59, 36, 848240), 'xb4a675': datetime.datetime(2024, 3, 5, 11, 59, 36, 848244), 'x3736ea': 'SomeValue', 'x9110a0': 'outertypeone', 'xb51d82': '73304984-83c8-46bd-aaa2-c4b4f24ae165', 'x271a58': datetime.datetime(2024, 3, 5, 11, 59, 36, 848256), 'x9ee2aa': datetime.datetime(2024, 3, 5, 11, 59, 36, 848257), 'x1cec64': 'InnerEmbedded', 'x7bf7f4': 'inner', 'x076ad6': 'is_pet_of', 'x584e0c': [], 'xd0967c': 'f38cadd9-8b40-4524-a685-17ceb005f111', 'x66b61e': 'is_pet_of', 'xf5a073': [], 'xe4e115': 'ad5db063-3640-47e1-b0cb-d9013099f24b', 'x5b4eb0': 'is_pet_of', 'x6f28ef': [], 'x92abf5': '22d3de1a-d371-4e70-bf4b-a83749229745'}