from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import SUBTYPECOLOR


class Color:

    def __init__(self, color=None) -> None:
        self.color = color
        self.outline = color + "CC"
        self.fill = color + "00"
        self.text_color = color + "22"

    @classmethod
    def from_subtype(cls, subtype):
        return cls(color=SUBTYPECOLOR.get(subtype, '#000000'))
    