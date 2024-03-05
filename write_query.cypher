
        MATCH (x39afaf {uid: $xe7025c})

        MATCH (x31ef49 {uid: $x0469d4})

        MATCH (x30744c {uid: $x3090e2})
        CREATE (x3eb498:Person:BaseNode {uid: $x781f4b, label: $x63212b, real_type: $xea3356})

        CREATE (xe975ed:OuterTypeOne:BaseNode:Embedded:DeleteDetach {uid: $x312fe6, some_value: $xb303ba, real_type: $xb96db6})

        CREATE (x7378f3:Inner:BaseNode:Embedded:DeleteDetach {uid: $xbc9100, name: $x9db73b, real_type: $x42e294})

        CREATE (x7378f3)-[:INNER_HAS_PET {reverse_name: $x39523b, relation_labels: $x557ffa}]->(x39afaf)

        CREATE (xe975ed)-[:INNER]->(x7378f3)

        CREATE (xe975ed)-[:OUTER_ONE_HAS_PET {reverse_name: $x218428, relation_labels: $xbaf22e}]->(x31ef49)

        CREATE (x3eb498)-[:OUTER]->(xe975ed)

        CREATE (x3eb498)-[:PERSON_HAS_PET {reverse_name: $xc81edc, relation_labels: $x01e46a}]->(x30744c)
        
        
        return x3eb498{.uid, .label, .real_type}
        {'x781f4b': '07604ed7-85fd-48a3-9da6-0c498c4e5857', 'x63212b': 'John Smith', 'xea3356': 'person', 'x312fe6': '1a4bfe1f-b465-4407-9dcc-ff99d0c20932', 'xb303ba': 'SomeValue', 'xb96db6': 'outertypeone', 'xbc9100': 'cf76cb82-7ac4-4f21-93aa-5a8413908e38', 'x9db73b': 'InnerEmbedded', 'x42e294': 'inner', 'x39523b': 'is_pet_of', 'x557ffa': [], 'xe7025c': '446f9df4-dc0b-4cf3-a03f-9c6362c28b91', 'x218428': 'is_pet_of', 'xbaf22e': [], 'x0469d4': '1bb412fd-ee05-49bc-9c6b-c9e66e1e9124', 'xc81edc': 'is_pet_of', 'x01e46a': [], 'x3090e2': '671027e2-29a6-41bb-bb1d-0cd1a034d022'}