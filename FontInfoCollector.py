from pathlib import Path
from typing import Callable

from fontTools.ttLib import TTCollection, TTFont, TTLibError, sfnt

from global_var import DisplayCJKTablesList, DisplayUnicodeBlocksList, CJKGroup


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
        
        self.cjk_char_count = {}
        self.unicode_char_count = {}

    def extract_chars(self):
        self.char_list = set(chr(x) for x in self.font.getBestCmap().keys())
        self.char_uvs_list = set()

        uvs_table = self.font["cmap"].getcmap(0, 5)
        if uvs_table is None:
            return
        for base_unicode, vs_tuples in uvs_table.uvsDict.items():
            for vs_unicode, glyph_name in vs_tuples:
                vs_string = chr(base_unicode) + chr(vs_unicode)
                self.char_uvs_list.add(vs_string)

    def count_cjk_chars(self) -> tuple[dict[str, int], dict[str, int]]:
        """Count CJK characters in the font.

        Returns:
            A tuple containing two dictionaries:
            - [0] cjk_char_count: A dictionary of CJK encoding ID to character count.
            - [1] unicode_char_count: A dictionary of Unicode block ID to character count.
        """
        self.cjk_char_count = {}
        for table_id, table in DisplayCJKTablesList.get_all_tables().items():
            self.cjk_char_count[table_id] = len(table.get_overlap(self.char_list))

        self.unicode_char_count = {}
        for block_id, block in DisplayUnicodeBlocksList.get_ordered_blocks().items():
            self.unicode_char_count[block_id] = sum(
                1 for char in self.char_list if char in block.assigned_ranges
            )
        return self.cjk_char_count, self.unicode_char_count
    
    def get_diff_chars(self, in_set: set[str]) -> set[str]:
        return self.char_list.difference(in_set)

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
