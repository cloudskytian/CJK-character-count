from tkinter import *

from localise import get_localised_label
from global_var import DisplayLanguage

class ReusableListPopup:
    def __init__(self, master, lang: DisplayLanguage = DisplayLanguage.EN):
        """Prepare persistent popup elements (window, label, button)."""
        self.lang = lang

        self.master = master
        self.popup_font = ("Segoe UI", 12)

        # --- create popup (but keep it hidden initially) ---
        self.toplevel = Toplevel(master)
        self.toplevel.withdraw()  # hide until needed
        self.toplevel.title(
            get_localised_label(self.lang, "OpenType collection selection")
        )
        self.toplevel.minsize(400, 150)
        self.toplevel.maxsize(750, 350)

        # --- label ---
        self.label = Label(
            self.toplevel,
            text=get_localised_label(self.lang, "Pick font for counting:"),
            font=self.popup_font,
        )
        self.label.pack(pady=(12, 0))

    def get_index(self, options: list[str]) -> int | None:
        """Show the popup with the provided options and return selected index."""
        if not options:
            return None

        # --- build dropdown menu for this call ---
        ttc_name_var = StringVar(value=options[0])
        option_widget = OptionMenu(self.toplevel, ttc_name_var, *options)
        option_widget.config(font=self.popup_font, width=350)
        option_widget.pack(expand=True, padx=12)

        # --- OK button ---
        button = Button(
            self.toplevel,
            text=get_localised_label(self.lang, "OK"),
            font=self.popup_font,
            command=self.toplevel.destroy,
        )
        button.pack(pady=(0, 12))

        # --- show popup ---
        self.toplevel.deiconify()
        self.toplevel.grab_set()
        self.toplevel.wait_window()

        # --- get selection ---
        result_id = options.index(ttc_name_var.get())
        return result_id
