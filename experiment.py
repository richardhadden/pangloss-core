import datetime

from icecream import ic

from pangloss_core.models import BaseNode, RelationConfig, RelationModel, RelationTo


class Pet(BaseNode):
    pass


class Person(BaseNode):
    pets: RelationTo[Pet, RelationConfig(reverse_name="has_owner")]


class Nun(BaseNode):
    pass


class JuniorNun(Nun):
    pass


class DudeNunRelation(RelationModel):
    purchased_when: datetime.date


class Adult(BaseNode):
    nuns: RelationTo[
        Nun,
        RelationConfig(reverse_name="is_owned_by", relation_model=DudeNunRelation),
    ]


class Dude(Adult):
    pass


class Organisation(BaseNode):
    nuns: RelationTo[Nun, RelationConfig(reverse_name="is_owned_by")]


nun_has_owner = Nun.incoming_relations["is_owned_by"]

ic(Nun.incoming_relations)

# types_to_be_connected_to = set([Adult, Dude, Organisation])

# incoming_related_types = set([ir.origin_base_class for ir in nun_has_owner])

# assert types_to_be_connected_to.issubset(incoming_related_types)
