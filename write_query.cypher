
        MATCH (xc1c36b {uid: $x71694e})

        MATCH (x30d8ee {uid: $x7ec1ec})

        MATCH (x48b98a {uid: $x4a67e0})
        CREATE (x9f6b49:Person:BaseNode {uid: $x154abd, label: $x78220c, real_type: $xffff86, created_when: datetime(), modified_when: datetime()})

        CREATE (xb792c8:OuterTypeOne:BaseNode:Embedded:DeleteDetach {uid: $xb7f337, some_value: $xffdf82, real_type: $xcff180, created_when: datetime(), modified_when: datetime()})

        CREATE (x13a0f3:Inner:BaseNode:Embedded:DeleteDetach {uid: $x0b596c, name: $xc29469, real_type: $xd26e33, created_when: datetime(), modified_when: datetime()})

        CREATE (x13a0f3)-[:INNER_HAS_PET {reverse_name: $xf9366d, relation_labels: $x6912a7}]->(xc1c36b)

        CREATE (xb792c8)-[:INNER]->(x13a0f3)

        CREATE (xb792c8)-[:OUTER_ONE_HAS_PET {reverse_name: $xe6f76f, relation_labels: $x3b182f}]->(x30d8ee)

        CREATE (x9f6b49)-[:OUTER]->(xb792c8)

        CREATE (x9f6b49)-[:PERSON_HAS_PET {reverse_name: $x5ad38e, relation_labels: $xf30674}]->(x48b98a)
        
        
        return x9f6b49{.uid, .label, .real_type}
        {'x154abd': '230b0754-681b-4f57-840d-2b532e92c2e3', 'x78220c': 'John Smith', 'xffff86': 'person', 'xb7f337': 'f77621da-41f3-4e70-a137-34f1da632d1c', 'xffdf82': 'SomeValue', 'xcff180': 'outertypeone', 'x0b596c': '1534f9b5-eb7f-4b02-a6f5-4c4aac819c0d', 'xc29469': 'InnerEmbedded', 'xd26e33': 'inner', 'xf9366d': 'is_pet_of', 'x6912a7': [], 'x71694e': '71408889-4daf-4c56-90f9-0c67cc2dcf11', 'xe6f76f': 'is_pet_of', 'x3b182f': [], 'x7ec1ec': '4b2c66f8-5bf6-4a90-b0c5-1ea666a6ed47', 'x5ad38e': 'is_pet_of', 'xf30674': [], 'x4a67e0': '697414be-862c-47e7-bf56-d2db4dfacd4f'}