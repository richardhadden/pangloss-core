
        MATCH (xf56712 {uid: $x4d943e})

        MATCH (x3d1e45 {uid: $xf7770b})

        MATCH (x1dc427 {uid: $xa241b2})
        CREATE (x391f2c:Order:BaseNode {uid: $xbb8290, label: $x12f201, real_type: $xb99bc2})

        CREATE (x108762:Order:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x9d0542, label: $x1eb277, real_type: $x306f18})

        CREATE (x98eb47:Payment:BaseNode:CreateInline:ReadInline:EditInline:DeleteDetach {uid: $x10c8e4, label: $xe86dd6, how_much: $xef5a81, real_type: $x75084f})

        CREATE (x98eb47)-[:PAYMENT_MADE_BY {reverse_name: $x87c427, relation_labels: $xf26750}]->(xf56712)

        CREATE (x108762)-[:THING_ORDERED]->(x98eb47)

        CREATE (x108762)-[:CARRIED_OUT_BY {reverse_name: $xe640e3, relation_labels: $xdbac4f}]->(x3d1e45)

        CREATE (x391f2c)-[:THING_ORDERED]->(x108762)

        CREATE (x391f2c)-[:CARRIED_OUT_BY {reverse_name: $x10aac3, relation_labels: $x223b0a}]->(x1dc427)
        
        
        return x391f2c{.uid, .label, .real_type}
        {'xbb8290': '625876b9-9bc8-4df6-ad2e-737cbeb206b8', 'x12f201': 'John Smith orders Toby Jones to order Olive Branch to make a payment', 'xb99bc2': 'order', 'x9d0542': 'de4f0fcd-54cf-474a-b2d6-2ec847826f13', 'x1eb277': 'Toby Jones orders Olive Branch to make a payment', 'x306f18': 'order', 'x10c8e4': '7bac351f-e409-4ab1-9d7a-39a5a6dcb74a', 'xe86dd6': 'Olive Branch makes payment', 'xef5a81': 1, 'x75084f': 'payment', 'x87c427': 'made_payment', 'xf26750': [], 'x4d943e': 'fc0f0ccb-c8cd-4ac3-980e-44a77a75b3a3', 'xe640e3': 'carried_out_order', 'xdbac4f': [], 'xf7770b': '113b5d69-c2fc-455c-8a54-c4f422af041d', 'x10aac3': 'carried_out_order', 'x223b0a': [], 'xa241b2': '54427fd0-ba1c-499a-9187-631a94eecd7a'}