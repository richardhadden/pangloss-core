from pangloss_core_new.model_setup.models_base import CamelModel


class RelationPropertiesModel(CamelModel):
    """Parent class for relationship properties

    TODO: Check types on subclassing, to make sure only viable literals allowed"""

    real_type: str
