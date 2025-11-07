from global_var import DisplayLanguage

LABELS = {
    DisplayLanguage.EN: {
        "CJK Character Count": "CJK Character Count",
        "Open": "Open",
        "Save Report": "Save Report",
        "text_report": "Text report",
        "section_titles": {
            "jian": "Chinese (Simp) Encodings",
            "jianfan": "Chinese (Simp/Trad) Encodings",
            "fan": "Chinese (Trad) Encodings",
            "uni": "Unicode Blocks",
        },
        "Font: ": "Font: ",
        "File: ": "File: ",
        "Select font file": "Select font file",
        "no_file_selected": "No file",
        "no_file_selected_message": "No font file selected.",
        "not_a_valid_font_file": "Not a valid font",
        "not_a_valid_font_file_message": "This is not a valid font file.",
        "report_saved": "Report saved",
        "report_saved_message": "Report successfully saved to: {}",
        "filetypes": {
            "*.ttf *.otf *.woff *.woff2 *.otc *.ttc": "All suppported font format",
            "*.ttf *.otf *.woff *.woff2": "Single font file format",
            "*.ttf": "TrueType font",
            "*.otf": "OpenType font",
            "*.woff *.woff2": "Web Open Font Format (WOFF)",
            "*.otc *.ttc": "OpenType collection font",
            "*.*": "All files",
        },
        "File": "File",
        "Language": "Language",
        "OpenType collection selection": "OpenType Collection Selection",
        "Pick font for counting:": "Pick font for counting:",
        "OK": "OK",
    },
    DisplayLanguage.ZHS: {
        "CJK Character Count": "字体计数软件",
        "Open": "打开",
        "Save Report": "保存报告",
        "text_report": "文本报告",
        "section_titles": {
            "jian": "简体中文编码",
            "jianfan": "简体/繁体中文编码",
            "fan": "繁体中文编码",
            "uni": "统一码区段",
        },
        "Font: ": "字体：",
        "File: ": "文件：",
        "Select font file": "选择字体文件",
        "no_file_selected": "没有文件",
        "no_file_selected_message": "未选择字体文件。",
        "not_a_valid_font_file": "不是有效的字体",
        "not_a_valid_font_file_message": "这不是有效的字体文件。",
        "report_saved": "报告已保存",
        "report_saved_message": "报告已成功保存至：{}",
        "filetypes": {
            "*.ttf *.otf *.woff *.woff2 *.otc *.ttc": "所有支援的字体格式",
            "*.ttf *.otf *.woff *.woff2": "单独字体文件",
            "*.ttf": "TrueType 字体",
            "*.otf": "OpenType 字体",
            "*.woff *.woff2": "网页开放字体 (WOFF)",
            "*.otc *.ttc": "OpenType 合集字型",
            "*.*": "所有文件",
        },
        "File": "文件",
        "Language": "语言",
        "OpenType collection selection": "OpenType合集字体选择",
        "Pick font for counting:": "选择计数的字体：",
        "OK": "确定",
    },
    DisplayLanguage.ZHT: {
        "CJK Character Count": "字型計數軟體",
        "Open": "打開",
        "Save Report": "保存報告",
        "text_report": "文本報告",
        "section_titles": {
            "jian": "簡體中文編碼",
            "jianfan": "簡體/正體（繁體）中文編碼",
            "fan": "正體（繁體）中文編碼",
            "uni": "統一碼區段",
        },
        "Font: ": "字型：",
        "File: ": "文檔：",
        "Select font file": "選擇字型文件",
        "no_file_selected": "沒有文件",
        "no_file_selected_message": "未選擇字型文件。",
        "not_a_valid_font_file": "不是有效的字型",
        "not_a_valid_font_file_message": "這不是有效的字型文件。",
        "report_saved": "報告已保存",
        "report_saved_message": "報告已成功保存至：{}",
        "filetypes": {
            "*.ttf *.otf *.woff *.woff2 *.otc *.ttc": "所有支援的字型格式",
            "*.ttf *.otf *.woff *.woff2": "單獨字型文件",
            "*.ttf": "TrueType 字型",
            "*.otf": "OpenType 字型",
            "*.woff *.woff2": "網頁開放字型 (WOFF)",
            "*.otc *.ttc": "OpenType 合集字型",
            "*.*": "所有文件",
        },
        "File": "文件",
        "Language": "語言",
        "OpenType collection selection": "OpenType合集字型選擇",
        "Pick font for counting:": "選擇計數的字型：",
        "OK": "確定",
    },
}


def get_localised_label(lang_code: DisplayLanguage, label_key: str):
    """Retrieve the localized label for the given language code and label key."""
    result = LABELS.get(lang_code, LABELS[DisplayLanguage.EN]).get(label_key, label_key)
    if isinstance(result, dict):
        return result.copy()
    if result is None:
        return label_key
    return result
