import datetime
from typing import Annotated

from annotated_types import MinLen, MaxLen

from pangloss_core.models import BaseNode, RelationTo, RelationConfig, ModelManager


def test_inheritance_override_bug():
    class Entity(BaseNode):
        __abstract__ = True

    class Person(Entity):
        pass

    class Statement(BaseNode):
        __abstract__ = True

        subject_of_statement: Annotated[
            RelationTo[Person],
            RelationConfig(reverse_name="is_subject_of_statement"),
        ]

    class TemporalStatement(Statement):
        __abstract__ = True
        when: datetime.date

    class Naming(Statement):
        first_name: str
        last_name: str

    class Birth(TemporalStatement):
        person_born: Annotated[
            RelationTo[Person],
            RelationConfig(
                reverse_name="has_birth_event",
                subclasses_relation="subject_of_statement",
                validators=[MinLen(1), MaxLen(1)],
            ),
        ]

    class Death(TemporalStatement):
        person_died: Annotated[
            RelationTo[Person],
            RelationConfig(
                reverse_name="has_death_event",
                subclasses_relation="subject_of_statement",
                validators=[MinLen(1), MaxLen(1)],
            ),
        ]

    ModelManager.initialise_models(depth=3)

    assert "subject_of_statement" in Naming.model_fields
    assert "subject_of_statement" in Naming.Edit.model_fields

    assert "person_born" not in Naming.model_fields
    assert "person_born" not in Naming.Edit.model_fields

    ## This is not a problem; just an issue with the API docs
