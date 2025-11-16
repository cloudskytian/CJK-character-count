from global_var import (
    DisplayCJKTablesList,
    CJKGroup,
    CJKTable,
    DisplayLanguage,
    DisplayUnicodeBlocksList,
)
from localise import get_localised_label

import csv
from pathlib import Path


def write(
    output_fullpath: Path, cjk_char_count, unicode_char_count, lang: DisplayLanguage
):

    output_file = output_fullpath.open("w", encoding="utf-8", newline="")
    # newline="" lets csv module control newlines
    output_writer = csv.DictWriter(
        output_file, ("name", "count", "full_size"), quotechar="'",
    )

    cjk_output_order = [CJKGroup.FAN, CJKGroup.JIANFAN, CJKGroup.JIAN]
    if lang == DisplayLanguage.ZHS:
        cjk_output_order = [CJKGroup.JIAN, CJKGroup.JIANFAN, CJKGroup.FAN]

    for table_group in cjk_output_order:
        write_table(
            output_writer,
            lang,
            get_localised_label(lang, "section_titles")[table_group],
            DisplayCJKTablesList.get_ordered_tables_in_group(table_group),
            cjk_char_count,
        )
        output_file.write("\n")

    output_file.write("\n")

    write_block(
        output_writer,
        lang,
        unicode_char_count,
    )

    output_file.write("\n")

    output_file.close()


def write_table(
    output_writer: csv.DictWriter,
    lang: DisplayLanguage,
    title: str,
    name_list: dict[str, CJKTable],
    count_arr: dict[str, int],
):
    output_writer.writerow({"name": "===", "count": title, "full_size": "==="})

    # language localization header
    if lang == DisplayLanguage.ZHS:
        csv_header = {"name": "#名称", "count": "计数", "full_size": "总数"}
    elif lang == DisplayLanguage.ZHT:
        csv_header = {"name": "#名稱", "count": "計數", "full_size": "總數"}
    else:
        csv_header = {"name": "#name", "count": "count", "full_size": "full_size"}
    output_writer.writerow(csv_header)

    # contents
    write_dict = []
    for varname, table in name_list.items():
        write_dict.append(
            {
                "name": '"' + table.localised_name(lang) + '"',
                "count": count_arr[varname],
                "full_size": table.count,
            }
        )
    output_writer.writerows(write_dict)


def write_block(
    output_writer: csv.DictWriter,
    lang: DisplayLanguage,
    count_arr: dict[str, int],
):
    output_writer.writerow(
        {
            "name": "===",
            "count": get_localised_label(lang, "section_titles.uni"),
            "full_size": "===",
        }
    )

    # language localization header
    if lang == DisplayLanguage.ZHS:
        csv_header = {"name": "#名称", "count": "计数", "full_size": "总数"}
    elif lang == DisplayLanguage.ZHT:
        csv_header = {"name": "#名稱", "count": "計數", "full_size": "總數"}
    else:
        csv_header = {"name": "#name", "count": "count", "full_size": "full_size"}
    output_writer.writerow(csv_header)

    write_dict = []
    for varname, block in DisplayUnicodeBlocksList.get_ordered_blocks().items():
        write_dict.append(
            {
                "name": '"' + get_localised_label(lang, "unicode_blocks").get(block.name, block.name) + '"',
                "count": count_arr[varname],
                "full_size": len(block.assigned_ranges),
            }
        )
    output_writer.writerows(write_dict)
