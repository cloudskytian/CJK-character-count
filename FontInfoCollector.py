

from fontTools.ttLib import TTCollection, TTFont, TTLibError, sfnt


from pathlib import Path
from typing import Callable


def get_ttc_list(filename: str) -> list[str]:
    # clear font list
    ttc_names = []
    # lazy=True: https://github.com/fonttools/fonttools/issues/2019
    ttc = TTCollection(filename, lazy=True)
    for font in ttc:
        # single font name in getName(nameID, platformID, platEncID, langID=None), 0x409 make sure all font in English name
        ttf_name = font["name"].getName(4, 3, 1, 0x409)
        # add the font name itself instead of the XML representation
        ttc_names.append(str(ttf_name))
    # return array of names
    return ttc_names


class FontInfoCollector:
    def __init__(self, font_path: Path, font_id: int = -1):
        self.font_path = font_path
        self.font_id = font_id
        try:
            self.font = TTFont(
                font_path, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=font_id
            )
        except TTLibError as e:
            raise ValueError(f"Failed to load font: {e}") from e
        self.font_name = self.font["name"].getBestFullName()
        self.char_list = set()
        self.char_uvs_list = set()
        self.extract_chars()

    def extract_chars(self):
        self.char_list = set(self.font.getBestCmap().keys())
        self.char_uvs_list = set()

        uvs_table = self.font["cmap"].getcmap(0, 5)
        if uvs_table is None:
            return
        for base_unicode, vs_tuples in uvs_table.uvsDict.items():
            for vs_unicode, glyph_name in vs_tuples:
                vs_string = chr(base_unicode) + chr(vs_unicode)
                self.char_uvs_list.add(vs_string)

    @classmethod
    def load_font(cls, font_path: Path, ttc_method: Callable[[list[str]], int]):
        font_id = -1
        try:
            with open(font_path, "rb") as f:
                headers = sfnt.readTTCHeader(f)
            if headers is not None:
                font_id = ttc_method(get_ttc_list(font_path))
        except TTLibError:
            pass
        return cls(font_path, font_id)