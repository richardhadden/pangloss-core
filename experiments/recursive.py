from pydantic import create_model, BaseModel
import typing


def create(c):
    m = create_model("ThingEdit", thing=(typing.Union["ThingEdit", OtherThing], ...))
    return m


class OtherThing(BaseModel):
    pass


class Thing(BaseModel):
    thing: "Thing"


t = create(Thing)
t.model_rebuild()
print(t.model_fields)
