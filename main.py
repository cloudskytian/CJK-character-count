from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox

import argparse
from pathlib import Path
from enum import StrEnum
from pydantic import BaseModel
import pyperclip

import global_var
from global_var import DisplayLanguage
import list_popup
from localise import get_localised_label
from FontInfoCollector import FontInfoCollector


__version__ = "0.50"


class ColourTheme(StrEnum):
    LIGHT = "light"
    DARK = "dark"


class CopyTypeOnClick(StrEnum):
    MISSING_CHARACTERS = "missing"
    CHARACTERS_IN_FONT = "in_font"


class SettingsManager(BaseModel):
    """Simple settings manager: load/save a JSON settings file and apply theme to a Tk root."""

    _path = Path(global_var.main_directory) / "settings.json"

    theme: ColourTheme = ColourTheme.LIGHT
    language: DisplayLanguage = DisplayLanguage.EN
    copy_type_on_click: CopyTypeOnClick = CopyTypeOnClick.MISSING_CHARACTERS

    @classmethod
    def load(cls):
        try:
            path = cls._path.default
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    return cls.model_validate_json(f.read())
            else:
                return cls()
        except Exception as e:
            from traceback import print_exc

            print_exc()
            pass

    def _save(self):
        try:
            path = self._path
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=None, ensure_ascii=False))
        except Exception:
            pass

    def __setattr__(self, key, value):
        res = super().__setattr__(key, value)
        if key in self.__annotations__:
            key_class = self.__annotations__.get(key, None)
            if key_class and issubclass(key_class, StrEnum):
                value = key_class(value)
            res = super().__setattr__(key, value)
            # only save if this is a explicitly defined attribute
            self._save()
        return res


# optional font loader (pyglet) — used to register local ttf/ttc files so Tk can use their family names
try:
    from pyglet.font import add_file as _pyglet_add_file

    tc_font_files = [
        global_var.main_directory / "GenYoGothicTW-R.ttf",
        global_var.main_directory / "cjk-char-header.ttf",
    ]
    for p in tc_font_files:
        if p.exists():
            _pyglet_add_file(str(p))
except Exception:
    pass


class CJKApp:
    def __init__(self, args):
        self.root = Tk()
        # starting window size
        self.root.geometry("1600x800")
        # minimum window size
        self.root.minsize(600, 600)
        # set up icon
        self.root.iconbitmap("appicon.ico")

        # Application state variables
        self.settings_mgr = SettingsManager.load()
        self.language_var = StringVar(self.root, value=self.settings_mgr.language)
        self.theme_var = StringVar(self.root, value=self.settings_mgr.theme)
        self.copy_on_click_var = StringVar(
            self.root, value=self.settings_mgr.copy_type_on_click.value
        )

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
                if args.report:
                    self.save_csv()
            except Exception:
                pass

    def _register_ui_fonts_by_language(self):
        """Attempt to register UI fonts for `lang` and set instance font tuples."""
        # keep instance attributes in sync
        lang = self.language_var.get()
        if lang == DisplayLanguage.ZHT:
            self.title_font = ("cjk-char-header", 14, "underline")
            self.text_font = ("GenYoGothic TW R", 13)
            self.text_sum_font = ("cjk-char-header", 13)
        elif lang == DisplayLanguage.ZHS:
            self.title_font = ("Microsoft YaHei UI", 14, "bold underline")
            self.text_font = ("Microsoft YaHei UI", 13)
            self.text_sum_font = ("Microsoft YaHei UI", 13, "bold")
        else:
            self.title_font = ("Segoe UI", 12, "bold underline")
            self.text_font = ("Segoe UI", 12)
            self.text_sum_font = ("Segoe UI", 12, "bold")

    # settings load/save and theming are provided by SettingsManager
    def _apply_theme(self, theme: str | ColourTheme | None = None):
        if theme is None:
            theme = self.theme_var.get()
        if theme == ColourTheme.DARK:
            bg = "#1e1e1e"
            fg = "#e6e6e6"
            widget_bg = "#2b2b2b"
        else:
            bg = "#ffffff"
            fg = "#000000"
            widget_bg = "#f0f0f0"

        try:
            self.root.configure(bg=bg)
        except Exception:
            pass

        def _apply(w):
            try:
                cls = w.winfo_class()
                if cls in ("Frame", "Label", "Button", "Canvas", "Scrollbar"):
                    try:
                        w.configure(bg=widget_bg)
                    except Exception:
                        pass
                if cls in ("Label", "Button"):
                    try:
                        w.configure(fg=fg)
                    except Exception:
                        pass
            except Exception:
                pass
            for c in w.winfo_children():
                _apply(c)

        try:
            _apply(self.root)
        except Exception:
            pass

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
                    lambda e, enc_key=enc_key: self.copy_charset_diff_to_clipboard(
                        enc_key
                    ),
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
        Label(container, text=self._("section_titles.uni"), font=self.title_font).grid(
            column=unicode_col, row=2, sticky=W, padx=5
        )
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

        # bind shortcuts
        self.root.bind_all("<Control-o>", lambda e: self.open_file(None))
        self.root.bind_all("<Control-s>", lambda e: self.save_csv())

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

        # finally, apply theme to new widgets
        self._apply_theme(self.settings_mgr.theme)

    def rebuild_ui(self):
        for w in self.frame.winfo_children():
            w.destroy()

        self._register_ui_fonts_by_language()
        self.build_ui()

    def _on_theme_change(self):
        # theme_var is a StringVar bound to menu; delegate to SettingsManager
        t = self.theme_var.get()
        try:
            self.settings_mgr.theme = t
            self._apply_theme(t)
        except Exception:
            pass

    def _on_language_change(self, lang):
        """Persist language selection and rebuild UI."""
        try:
            # lang may be DisplayLanguage enum; store its value
            self.settings_mgr.language = DisplayLanguage(lang)
            self.language_var.set(lang)
            # update fonts/layout and rebuild
            self.rebuild_ui()
        except Exception:
            pass

    def _on_copy_on_click_change(self):
        """Persist copy on click selection."""
        try:
            cotc = self.copy_on_click_var.get()
            self.settings_mgr.copy_type_on_click = CopyTypeOnClick(cotc)
        except Exception:
            pass

    def _build_menubar(self):
        # root menu bar
        top_menu_bar = Menu(self.root)
        self.root.config(menu=None)
        self.root.config(menu=top_menu_bar)

        # File menu
        file_menu = Menu(top_menu_bar, tearoff=0)
        top_menu_bar.add_cascade(label=self._("menu.file"), menu=file_menu)
        file_menu.add_command(
            label=self._("menu.open"),
            command=lambda: self.open_file(),
        )
        file_menu.add_command(
            label=self._("menu.save"),
            command=lambda: self.save_csv(),
        )

        # Settings menu
        settings_menu = Menu(top_menu_bar, tearoff=0)
        top_menu_bar.add_cascade(label=self._("menu.settings"), menu=settings_menu)

        # Settings menu (theme)
        theme_sub = Menu(settings_menu, tearoff=0)
        theme_sub.add_radiobutton(
            label=self._("menu.light"),
            variable=self.theme_var,
            value=ColourTheme.LIGHT,
            command=self._on_theme_change,
        )
        theme_sub.add_radiobutton(
            label=self._("menu.dark"),
            variable=self.theme_var,
            value=ColourTheme.DARK,
            command=self._on_theme_change,
        )
        settings_menu.add_cascade(label=self._("menu.theme"), menu=theme_sub)

        # UI localisation menu
        language_sub = Menu(settings_menu, tearoff=0)
        for lang in global_var.DisplayLanguage:
            language_sub.add_radiobutton(
                label=lang.display_name(),
                variable=self.language_var,
                value=lang.value,
                command=lambda l=lang: self._on_language_change(l),
            )
        settings_menu.add_cascade(label=self._("menu.language"), menu=language_sub)

        # copy on click menu
        copy_type_sub = Menu(settings_menu, tearoff=0)
        copy_type_sub.add_radiobutton(
            label=self._("menu.Missing Characters"),
            variable=self.copy_on_click_var,
            value=CopyTypeOnClick.MISSING_CHARACTERS,
            command=self._on_copy_on_click_change,
        )
        copy_type_sub.add_radiobutton(
            label=self._("menu.Characters in Font"),
            variable=self.copy_on_click_var,
            value=CopyTypeOnClick.CHARACTERS_IN_FONT,
            command=self._on_copy_on_click_change,
        )
        settings_menu.add_cascade(
            label=self._("menu.Copy on Click"), menu=copy_type_sub
        )

        # File menu
        about_menu = Menu(top_menu_bar, tearoff=0)
        top_menu_bar.add_cascade(label=self._("menu.about"), menu=about_menu)
        about_menu.add_command(
            label=self._("menu.about"),
            command=lambda: messagebox.showinfo(
                title=self._("menu.about") + " " + self._("CJK Character Count"),
                message=f"{self._('CJK Character Count')}\n{self._('menu.version')} {__version__}",
            ),
        )

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
        if self.last_font is None or self.font_name.get() == self._("no_file_selected"):
            messagebox.showwarning(
                title=self._("no_file_selected"),
                message=self._("no_file_selected_message"),
            )
            return

        save_file_path = fd.asksaveasfilename(
            title=self._("Save Report"),
            defaultextension=".csv",
            initialfile=self.last_font.font_path.stem + ".csv",
            filetypes=[
                ("CSV file", "*.csv"),
                ("HTML file", "*.html"),
                ("All files", "*.*"),
            ],
        )
        if not save_file_path:
            return

        write_module = None
        # convert to resolved Path
        save_file_path = Path(save_file_path).resolve()
        if save_file_path.suffix.lower() == ".html":
            import write_html

            write_module = write_html.write
        elif save_file_path.suffix.lower() == ".csv":
            import write_csv

            write_module = write_csv.write
        else:
            messagebox.showwarning(
                title=self._("invalid_file_extension"),
                message=self._("invalid_file_extension_message"),
            )
            return

        write_module(
            save_file_path,
            self.last_font.cjk_char_count,
            self.last_font.unicode_char_count,
            self.language_var.get(),
        )

        messagebox.showinfo(
            title=self._("report_saved"),
            message=self._("report_saved_message").format(save_file_path),
        )

    def copy_charset_diff_to_clipboard(self, encoding_id: str):
        # validate
        if self.last_font is None:
            return
        table = global_var.DisplayCJKTablesList.get_all_tables().get(encoding_id, None)
        if not table:
            return

        # get diff
        copying_style = ""
        result_set = set()
        if self.settings_mgr.copy_type_on_click == CopyTypeOnClick.MISSING_CHARACTERS:
            # copy missing characters
            result_set = table.get_diff(self.last_font.char_list)
            copying_style = "missing"
        else:
            # copy characters in font and encoding
            result_set = table.get_overlap(self.last_font.char_list)
            copying_style = "overlap"
        pyperclip.copy("".join(sorted(result_set)))

        # popup message
        messagebox.showinfo(
            title=self._("copied_to_clipboard"),
            message=self._("copied_to_clipboard_message_" + copying_style).format(
                count=len(result_set),
            ),
        )

    def run(self):
        self.root.mainloop()

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
    app = CJKApp(args)
    app.run()
