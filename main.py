from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox

import os
import sys
import argparse
from pathlib import Path


from FontInfoCollector import FontInfoCollector
import count_char
import global_var
from global_var import DisplayLanguage
import list_popup
from localise import get_localised_label

# optional font loader (pyglet) — used to register local ttf/ttc files so Tk can use their family names
try:
    from pyglet.font import add_file as _pyglet_add_file

    PYGLET_AVAILABLE = True
except Exception:
    _pyglet_add_file = None
    PYGLET_AVAILABLE = False


if PYGLET_AVAILABLE:
    try:
        tc_font_files = [
            os.path.join(global_var.main_directory, "GenYoGothicTW-R.ttf"),
            os.path.join(global_var.main_directory, "cjk-char-bold.ttf"),
        ]
        for p in tc_font_files:
            if os.path.exists(p):
                _pyglet_add_file(p)
    except Exception:
        pass


class CJKApp:
    def __init__(self, root, args):
        self.root = root
        self.args = args

        # Application state variables
        self.language_var = StringVar(self.root, value=DisplayLanguage.EN)

        # fonts (defaults; may be changed by register_fonts_for_language)
        self.title_font = ("Segoe UI", 12, "bold underline")
        self.text_font = ("Segoe UI", 12)
        self.text_sum_font = ("Segoe UI", 12, "bold")

        # frame container
        self.frame = Frame(self.root)
        self.frame.pack(padx=(25, 40), pady=(0, 30))

        # Current font file display
        self.font_file_path = StringVar(self.root)
        self.font_name = StringVar(self.root)
        # persisted last result
        self.last_font = None
        self.last_cjk_counts = {}
        self.last_unicode_counts = {}

        self._register_ui_fonts_by_language()
        self._update_font_info_display()
        self.build_ui()

        # open file if provided on command line
        if args.filename and args.filename.lower().endswith(
            (".otf", ".ttf", ".woff", ".woff2", ".otc", ".ttc")
        ):
            try:
                self.open_file(args.filename)
                if self.args.report:
                    self.save_csv()
            except Exception:
                pass

    def _register_ui_fonts_by_language(self):
        """Attempt to register UI fonts for `lang` and set instance font tuples."""
        # keep instance attributes in sync
        lang = self.language_var.get()
        if lang == DisplayLanguage.ZHT:
            self.title_font = ("cjk-char-bold", 14, "underline")
            self.text_font = ("GenYoGothic TW R", 12)
            self.text_sum_font = ("cjk-char-bold", 12)
        elif lang == DisplayLanguage.ZHS:
            self.title_font = ("Microsoft YaHei UI", 14, "bold underline")
            self.text_font = ("Microsoft YaHei UI", 12)
            self.text_sum_font = ("Microsoft YaHei UI", 12, "bold")
        else:
            self.title_font = ("Segoe UI", 12, "bold underline")
            self.text_font = ("Segoe UI", 12)
            self.text_sum_font = ("Segoe UI", 12, "bold")

    def build_ui(self):
        """Create UI in `container` according to language `lang`."""
        container = self.frame
        lang = self.language_var.get()

        # rebuild menu bar to change language
        self._build_menubar()

        # reset vars
        self.cjk_label_var = {}
        self.unicode_label_var = {}

        self.root.title(self._("CJK Character Count"))

        # Top controls
        btn = Button(
            container,
            text=self._("Open"),
            font=self.text_font,
            command=lambda: self.open_file(None),
        )
        btn.grid(column=2, row=0, sticky=E)

        # Font Info display
        font_name_lbl = Label(
            container, textvariable=self.font_name, justify="left", font=self.text_font
        )
        font_name_lbl.grid(column=0, row=0, sticky=W, columnspan=2)
        font_file_lbl = Label(
            container,
            textvariable=self.font_file_path,
            justify="left",
            font=self.text_font,
        )
        font_file_lbl.grid(column=3, row=0, sticky=W, columnspan=3)

        # language-specific data
        if lang == DisplayLanguage.ZHT:
            order = ["fan", "jianfan", "jian"]
            cjk_lists = {
                "fan": global_var.cjk_fan_list_zht,
                "jianfan": global_var.cjk_jian_fan_list_zht,
                "jian": global_var.cjk_jian_list_zht,
            }
            unicode_list = global_var.unicode_list_zht
        elif lang == DisplayLanguage.ZHS:
            order = ["jian", "jianfan", "fan"]
            cjk_lists = {
                "jian": global_var.cjk_jian_list_zhs,
                "jianfan": global_var.cjk_jian_fan_list_zhs,
                "fan": global_var.cjk_fan_list_zhs,
            }
            unicode_list = global_var.unicode_list_zhs
        else:
            order = ["fan", "jianfan", "jian"]
            cjk_lists = {
                "jian": global_var.cjk_jian_list_en,
                "jianfan": global_var.cjk_jian_fan_list_en,
                "fan": global_var.cjk_fan_list_en,
            }
            unicode_list = global_var.unicode_list

        # Build sections
        row_cursor = 2
        for section in order:
            Label(
                container,
                text=self._("section_titles")[section],
                font=self.title_font,
                anchor="w",
            ).grid(column=0, row=row_cursor, sticky=W, padx=5)
            row_cursor += 1
            for i, (enc_key, enc_label) in enumerate(
                cjk_lists.get(section, {}).items()
            ):
                self.cjk_label_var[enc_key] = StringVar(self.root)
                Label(
                    container,
                    text=enc_label + "：",
                    justify="left",
                    font=self.text_font,
                ).grid(column=0, row=row_cursor, sticky=W)
                table_count_label = Label(
                    container,
                    textvariable=self.cjk_label_var[enc_key],
                    font=self.text_font,
                )
                table_count_label.grid(column=1, row=row_cursor, sticky=E)
                table_count_label.bind(
                    "<Button-1>",
                    lambda e, lbl=table_count_label: print(e, lbl.cget("text")),
                )
                Label(
                    container,
                    text="/" + str(global_var.cjk_count.get(enc_key, "")),
                    justify="left",
                    font=self.text_font,
                ).grid(column=2, row=row_cursor, sticky=W)
                row_cursor += 1
            row_cursor += 1

        # Unicode section
        unicode_col = 4
        Label(
            container, text=self._("section_titles")["uni"], font=self.title_font
        ).grid(column=unicode_col, row=2, sticky=W, padx=5)
        for i, (u_key, u_label) in enumerate(unicode_list.items()):
            u_row = i + 3
            self.unicode_label_var[u_key] = StringVar(self.root)
            u_font = self.text_sum_font if u_key == "total" else self.text_font
            Label(container, text=u_label + "：", justify="left", font=u_font).grid(
                column=unicode_col, row=u_row, sticky=W
            )
            Label(
                container,
                textvariable=self.unicode_label_var[u_key],
                justify="right",
                font=u_font,
            ).grid(column=unicode_col + 1, row=u_row, sticky=E)
            Label(
                container,
                text="/" + str(global_var.unicode_count.get(u_key, "")),
                justify="left",
                font=u_font,
            ).grid(column=unicode_col + 2, row=u_row, sticky=W)

        # apply persisted counts
        self._update_font_info_display()
        for enc_key, var in self.cjk_label_var.items():
            try:
                var.set(self.last_cjk_counts.get(enc_key, 0))
            except Exception:
                pass
        for u_key, var in self.unicode_label_var.items():
            try:
                var.set(self.last_unicode_counts.get(u_key, 0))
            except Exception:
                pass

    def _build_menubar(self):
        top_menu_bar = Menu(self.root)
        self.root.config(menu=None)
        self.root.config(menu=top_menu_bar)

        # File menu
        file_menu = Menu(top_menu_bar, tearoff=0)
        file_menu.add_command(
            label=self._("Open"),
            command=lambda: self.open_file(),
        )
        file_menu.add_command(
            label=self._("Save Report"),
            command=lambda: self.save_csv(),
        )

        top_menu_bar.add_cascade(label=self._("File"), menu=file_menu)

        # UI localisation menu
        language_menu = Menu(top_menu_bar, tearoff=0)
        # add radiobuttons bound to the instance StringVar
        for lang in global_var.DisplayLanguage:
            language_menu.add_radiobutton(
                label=lang.display_name(),
                variable=self.language_var,
                value=lang.value,
                command=self.rebuild_ui,
            )
        top_menu_bar.add_cascade(label=self._("Language"), menu=language_menu)

    def rebuild_ui(self):
        for w in self.frame.winfo_children():
            w.destroy()

        self._register_ui_fonts_by_language()
        self.build_ui()

    def _update_font_info_display(self):
        """Update font info display labels."""
        self.font_file_path.set(
            self._("File: ")
            + (
                self.last_font.font_path.name
                if self.last_font
                else self._("no_file_selected")
            )
        )
        self.font_name.set(
            self._("Font: ")
            + (
                self.last_font.font_name
                if self.last_font
                else self._("no_file_selected")
            )
        )

    def open_file(self, filename_arg: str = None):
        if filename_arg:
            filename = Path(filename_arg).resolve()
        else:
            available_filetypes = [
                (filetype_name, filetype)
                for filetype, filetype_name in self._("filetypes").items()
            ]
            filename = Path(
                fd.askopenfilename(
                    initialdir="shell:Desktop",
                    title=self._("Select font file"),
                    filetypes=available_filetypes,
                )
            ).resolve()

        if filename is None or not filename.is_file():
            self.last_font = None
            self._update_font_info_display()
            messagebox.showwarning(
                title=self._("no_file_selected"),
                message=self._("no_file_selected_message"),
            )
            return

        try:
            self.last_font = FontInfoCollector.load_font(
                filename,
                ttc_method=lambda font_list: list_popup.ReusableListPopup(
                    self.root, self.language_var.get()
                ).get_index(font_list),
            )
            self._update_font_info_display()
        except ValueError:
            self.last_font = None
            self._update_font_info_display()
            messagebox.showwarning(
                title=self._("not_a_valid_font_file"),
                message=self._("not_a_valid_font_file_message"),
            )
            return

        # reset counters
        for cjk_enc in global_var.cjk_list:
            if cjk_enc in self.cjk_label_var:
                self.cjk_label_var[cjk_enc].set(0)
        for unicode_enc in global_var.unicode_list:
            if unicode_enc in self.unicode_label_var:
                self.unicode_label_var[unicode_enc].set(0)

        # import and count
        output = count_char.count_char(self.last_font.char_list)
        cjk_char_count, unicode_char_count = output[0], output[1]

        # persist last counts
        try:
            self.last_cjk_counts = dict(cjk_char_count)
            self.last_unicode_counts = dict(unicode_char_count)
        except Exception:
            self.last_cjk_counts = {}
            self.last_unicode_counts = {}

        for cjk_enc in global_var.cjk_list:
            if cjk_enc in self.cjk_label_var:
                self.cjk_label_var[cjk_enc].set(self.last_cjk_counts.get(cjk_enc, 0))
        for unicode_enc in global_var.unicode_list:
            self.unicode_label_var[unicode_enc].set(
                self.last_unicode_counts.get(unicode_enc, 0)
            )

        # 猫啃网专用HTML模板
        # import write_html
        # write_html.write(filename.name, cjk_char_count, unicode_char_count)

    def save_csv(self):
        import write_csv

        if self.font_name.get() == self._("no_file_selected"):
            messagebox.showwarning(
                title=self._("no_file_selected"),
                message=self._("no_file_selected_message"),
            )
            return

        save_csv_path = Path(
            fd.asksaveasfilename(
                title=self._("Save Report"),
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
        ).resolve()
        write_csv.write(
            save_csv_path,
            self.last_cjk_counts,
            self.last_unicode_counts,
            self.language_var.get(),
        )

        messagebox.showinfo(
            title=self._("report_saved"),
            message=self._("report_saved_message").format(save_csv_path),
        )

    def run(self):
        self.root.mainloop()

    def copy_text_to_clipboard(self, text: str):
        pass

    def _(self, label_key):
        """Retrieve the localized label for the given label key based on current language."""
        return get_localised_label(self.language_var.get(), label_key)


parser = argparse.ArgumentParser(
    prog="CJK Character Count (combined)",
    description="A program that parse a font file and list CJK characters. Supports EN/ZHT/ZHS UI and reorders sections accordingly.",
)
parser.add_argument("filename", nargs="?", default=None)
parser.add_argument(
    "-r",
    "--report",
    action="store_true",
    default=False,
    help="Output a .txt file with CSV structure under cjk_report folder.",
)
args = parser.parse_args()


if __name__ == "__main__":
    root = Tk()
    app = CJKApp(root, args)
    app.run()
