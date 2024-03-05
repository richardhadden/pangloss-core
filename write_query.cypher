
        MATCH (x810005 {uid: $x841ad6})

        MATCH (xd5b4fc {uid: $x8f4c72})

        MATCH (x508116 {uid: $x6db82a})
        CREATE (x2b6de3:Person:BaseNode {uid: $x56a45e, label: $x5a60aa, real_type: $x520035, created_when: datetime(), modified_when: datetime()})

        CREATE (xca9be5:OuterTypeOne:BaseNode:Embedded:DeleteDetach {uid: $xcff8ab, some_value: $xf0c25b, real_type: $x791317, created_when: datetime(), modified_when: datetime()})

        CREATE (x82f217:Inner:BaseNode:Embedded:DeleteDetach {uid: $x123813, name: $x390f56, real_type: $x6f315f, created_when: datetime(), modified_when: datetime()})

        CREATE (x82f217)-[:INNER_HAS_PET {reverse_name: $x74bdac, relation_labels: $xc9d849}]->(x810005)

        CREATE (xca9be5)-[:INNER]->(x82f217)

        CREATE (xca9be5)-[:OUTER_ONE_HAS_PET {reverse_name: $x13197e, relation_labels: $x89fe2f}]->(xd5b4fc)

        CREATE (x2b6de3)-[:OUTER]->(xca9be5)

        CREATE (x2b6de3)-[:PERSON_HAS_PET {reverse_name: $x525990, relation_labels: $x044543}]->(x508116)
        
        
        return x2b6de3{.uid, .label, .real_type}
        {'x56a45e': 'febb291a-9dfb-435a-9633-e5b74b310bfe', 'x5a60aa': 'John Smith', 'x520035': 'person', 'xcff8ab': '58373b09-e90c-486b-bcbe-1c35d96f91fe', 'xf0c25b': 'SomeValue', 'x791317': 'outertypeone', 'x123813': 'eddfb83e-d170-4db0-af3b-beb98f800918', 'x390f56': 'InnerEmbedded', 'x6f315f': 'inner', 'x74bdac': 'is_pet_of', 'xc9d849': [], 'x841ad6': '1a6def8f-6919-4a43-8033-9eae82ceef21', 'x13197e': 'is_pet_of', 'x89fe2f': [], 'x8f4c72': 'ac3654d3-b94e-4617-a5bb-a91598fbc622', 'x525990': 'is_pet_of', 'x044543': [], 'x6db82a': '7826f45d-3c09-456d-80c6-25c98f17fdcc'}