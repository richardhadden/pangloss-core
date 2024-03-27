from pangloss_core.models import BaseNode
from pangloss_core.model_setup.model_manager import ModelManager
from pangloss_core.translation import BuildTranslationBase


def test_translation_setup():
    Translation = BuildTranslationBase("en", "de")
    assert Translation.model_fields.keys() == {
        "de_description",
        "de_verbose_name",
        "de_verbose_name_plural",
        "en_description",
        "en_verbose_name",
        "en_verbose_name_plural",
    }


def test_translation():
    TranslationBase = BuildTranslationBase("en")

    class Translation(TranslationBase):
        en_verbose_name = "My Thing"
        en_verbose_name_plural = "My Things"
        en_description = "A nice model"
