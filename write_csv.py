import global_var
import csv
from pathlib import Path
from localise import get_localised_label


def write(output_fullpath: Path, cjk_char_count, unicode_char_count, lang):
    # language localization
    if lang == "zhs":  # simplified chinese
        cjk_jian_namelist = global_var.cjk_jian_list_zhs
        cjk_jian_fan_namelist = global_var.cjk_jian_fan_list_zhs
        cjk_fan_namelist = global_var.cjk_fan_list_zhs
        unicode_namelist = global_var.unicode_list_zhs
        csv_title = "#名称,计数,总数"
    elif lang == "zht":  # traditional chinese
        cjk_jian_namelist = global_var.cjk_jian_list_zht
        cjk_jian_fan_namelist = global_var.cjk_jian_fan_list_zht
        cjk_fan_namelist = global_var.cjk_fan_list_zht
        unicode_namelist = global_var.unicode_list_zht
        csv_title = "#名稱,計數,總數"
    else:
        cjk_jian_namelist = global_var.cjk_jian_list_en
        cjk_jian_fan_namelist = global_var.cjk_jian_fan_list_en
        cjk_fan_namelist = global_var.cjk_fan_list_en
        unicode_namelist = global_var.unicode_list
        csv_title = "#name,count,full_size"

    output_file = output_fullpath.open("w", encoding="utf-8", newline="")
    # newline="" lets csv module control newlines
    output_writer = csv.DictWriter(
        output_file, ("name", "count", "full_size"), quoting=csv.QUOTE_NONNUMERIC
    )

    # start writing
    if lang == "zht":
        write_list(
            output_file,
            output_writer,
            get_localised_label(lang, "section_titles")["fan"],
            csv_title,
            cjk_fan_namelist,
            cjk_char_count,
            global_var.cjk_count,
        )
    else:
        write_list(
            output_file,
            output_writer,
            get_localised_label(lang, "section_titles")["jian"],
            csv_title,
            cjk_jian_namelist,
            cjk_char_count,
            global_var.cjk_count,
        )

    output_file.write("===\n\n")

    write_list(
        output_file,
        output_writer,
        get_localised_label(lang, "section_titles")["jianfan"],
        csv_title,
        cjk_jian_fan_namelist,
        cjk_char_count,
        global_var.cjk_count,
    )

    output_file.write("===\n\n")

    if lang == "zht":
        write_list(
            output_file,
            output_writer,
            get_localised_label(lang, "section_titles")["jian"],
            csv_title,
            cjk_jian_namelist,
            cjk_char_count,
            global_var.cjk_count,
        )
    else:
        write_list(
            output_file,
            output_writer,
            get_localised_label(lang, "section_titles")["fan"],
            csv_title,
            cjk_fan_namelist,
            cjk_char_count,
            global_var.cjk_count,
        )

    output_file.write("===\n\n")

    write_list(
        output_file,
        output_writer,
        get_localised_label(lang, "section_titles")["uni"],
        csv_title,
        unicode_namelist,
        unicode_char_count,
        global_var.unicode_count,
    )

    output_file.write("===")

    output_file.close()


def write_list(
    output_file, output_writer, title, csv_title, name_list, count_arr, total_arr
):
    output_file.write(f"=== %s ===\n" % (title))
    write_dict = []
    for varname, fullname in name_list.items():
        write_dict.append(
            {
                "name": fullname,
                "count": count_arr[varname],
                "full_size": total_arr[varname],
            }
        )
    output_file.write(csv_title + "\n")
    output_writer.writerows(write_dict)
