from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox

import argparse
from pathlib import Path


import global_var
from global_var import DisplayLanguage
import list_popup
from localise import get_localised_label
from FontInfoCollector import FontInfoCollector

# optional font loader (pyglet) — used to register local ttf/ttc files so Tk can use their family names
try:
    import pyglet
    from pyglet.font import add_file as _pyglet_add_file

    # use legacy naming to avoid issues with certain font names
    pyglet.options["dw_legacy_naming"] = True

    try:
        tc_font_files = [
            global_var.main_directory / "GenYoGothicTW-R.ttf",
            global_var.main_directory / "cjk-char-bold.ttf",
        ]
        for p in tc_font_files:
            if p.exists():
                _pyglet_add_file(str(p))
    except Exception as e:
        print(e)
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

        # root container with canvas for scrolling
        root_frame = Frame(self.root)
        root_frame.pack(fill="both", expand=True)
        root_frame.grid_rowconfigure(0, weight=1)
        root_frame.grid_columnconfigure(0, weight=1)

        # only canvas can scroll
        canvas = Canvas(root_frame)
        canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        vscrollbar = Scrollbar(root_frame, orient="vertical", command=canvas.yview)
        vscrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=vscrollbar.set)

        # grid frame for display table
        self.frame = Frame(canvas, pady=10)
        # create window with anchor='n' (x coordinate is center when we set it)
        _frame_window = canvas.create_window((0, 0), window=self.frame, anchor="n")

        def _on_frame_config(event):
            # update scrollregion then recenter
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.update_idletasks()
                # center the frame: compute left x coordinate so frame is centered
                canvas_w = canvas.winfo_width()
                frame_w = self.frame.winfo_reqwidth()
                x = (canvas_w - frame_w) // 2
                canvas.coords(_frame_window, x, 0)
            except Exception:
                pass

        canvas.bind("<Configure>", _on_frame_config)

        # mouse wheel support (Windows)
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        def _bind_wheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(event):
            canvas.unbind_all("<MouseWheel>")

        self.frame.bind("<Enter>", _bind_wheel)
        self.frame.bind("<Leave>", _unbind_wheel)

        # Current font file display
        self.font_file_path = StringVar(self.root)
        self.font_name = StringVar(self.root)
        # persisted last result
        self.last_font = None

        self._register_ui_fonts_by_language()
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
            self.text_font = ("GenYoGothic TW R", 13)
            self.text_sum_font = ("cjk-char-bold", 13)
        elif lang == DisplayLanguage.ZHS:
            self.title_font = ("Microsoft YaHei UI", 14, "bold underline")
            self.text_font = ("Microsoft YaHei UI", 13)
            self.text_sum_font = ("Microsoft YaHei UI", 13, "bold")
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

        # CJK sections
        section_order = [
            global_var.CJKGroup.FAN,
            global_var.CJKGroup.JIANFAN,
            global_var.CJKGroup.JIAN,
        ]
        if lang == DisplayLanguage.ZHS:
            section_order = [
                global_var.CJKGroup.JIAN,
                global_var.CJKGroup.JIANFAN,
                global_var.CJKGroup.FAN,
            ]

        # Build sections
        row_cursor = 2
        for section_label in section_order:
            # Section title
            Label(
                container,
                text=self._("section_titles")[section_label],
                font=self.title_font,
            ).grid(column=0, row=row_cursor, sticky=W, padx=5)
            row_cursor += 1
            # Section entries
            for (
                enc_key,
                enc_info,
            ) in global_var.DisplayCJKTablesList.get_ordered_tables_in_group(
                section_label
            ).items():
                self.cjk_label_var[enc_key] = StringVar(self.root)
                Label(
                    container,
                    text=enc_info.localised_name(self.language_var.get()) + "：",
                    justify="left",
                    font=self.text_font,
                ).grid(column=0, row=row_cursor, sticky=W)
                table_count_label = Label(
                    container,
                    textvariable=self.cjk_label_var[enc_key],
                    justify="right",
                    font=self.text_font,
                )
                table_count_label.grid(column=1, row=row_cursor, sticky=E)
                table_count_label.bind(
                    "<Button-1>",
                    lambda e, lbl=table_count_label: print(e, lbl.cget("text")),
                )
                Label(
                    container,
                    text="/" + str(enc_info.count),
                    justify="left",
                    font=self.text_font,
                ).grid(column=2, row=row_cursor, sticky=W, padx=(0, 16))
                row_cursor += 1
            row_cursor += 1

        # Unicode section
        unicode_col = 4
        Label(
            container, text=self._("section_titles")["uni"], font=self.title_font
        ).grid(column=unicode_col, row=2, sticky=W, padx=5)
        for i, (uni_block_id, uni_block) in enumerate(
            global_var.DisplayUnicodeBlocksList.get_ordered_blocks().items()
        ):
            u_row = i + 3
            self.unicode_label_var[uni_block_id] = StringVar(self.root)
            u_font = self.text_sum_font if uni_block_id == "total" else self.text_font
            Label(
                container,
                text=self._("unicode_blocks").get(uni_block.name, uni_block.name)
                + "：",
                justify="left",
                font=u_font,
            ).grid(column=unicode_col, row=u_row, sticky=W)
            Label(
                container,
                textvariable=self.unicode_label_var[uni_block_id],
                justify="right",
                font=u_font,
            ).grid(column=unicode_col + 1, row=u_row, sticky=E)
            Label(
                container,
                text="/" + str(len(uni_block.assigned_ranges)),
                justify="left",
                font=u_font,
            ).grid(column=unicode_col + 2, row=u_row, sticky=W)

        # apply persisted counts
        self._update_font_info_display()
        self._reset_counts()
        if self.last_font:
            try:
                for enc_key, var in self.cjk_label_var.items():
                    var.set(self.last_font.cjk_char_count.get(enc_key, 0))
                for uni_block_id, var in self.unicode_label_var.items():
                    var.set(self.last_font.unicode_char_count.get(uni_block_id, 0))
            except Exception:
                pass

    def rebuild_ui(self):
        for w in self.frame.winfo_children():
            w.destroy()

        self._register_ui_fonts_by_language()
        self.build_ui()

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

    def _reset_counts(self):
        for label_var in self.cjk_label_var.values():
            label_var.set(0)
        for label_var in self.unicode_label_var.values():
            label_var.set(0)

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
            messagebox.showwarning(
                title=self._("not_a_valid_font_file"),
                message=self._("not_a_valid_font_file_message"),
            )
            return

        # reset counters
        self._reset_counts()

        # import and count
        cjk_char_count, unicode_char_count = self.last_font.count_cjk_chars()

        for cjk_enc in global_var.DisplayCJKTablesList.get_all_tables().keys():
            if cjk_enc in self.cjk_label_var:
                self.cjk_label_var[cjk_enc].set(cjk_char_count.get(cjk_enc, 0))
        for (
            unicode_enc
        ) in global_var.DisplayUnicodeBlocksList.get_ordered_blocks().keys():
            self.unicode_label_var[unicode_enc].set(
                unicode_char_count.get(unicode_enc, 0)
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
            self.last_font.cjk_char_count,
            self.last_font.unicode_char_count,
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
