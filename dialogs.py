import tkinter as tk
from tkinter import ttk
from functools import partial
import sv_ttk


def show_message(title="Title", details="Description", *, parent=None, icon=None):
    return popup(
        parent,
        title,
        details,
        icon,
        buttons=[("Yes", None, "default")],
    )


def ask_yes_no(title="Title", details="Description", *, parent=None, icon=None):
    return popup(
        parent,
        title,
        details,
        icon,
        buttons=[("开启", True, "accent"), ("关闭", False)],
    )

def popup(parent, title, details, icon, *, buttons):
    dialog = tk.Toplevel()

    result = None

    big_frame = ttk.Frame(dialog)
    big_frame.pack(fill="both", expand=True)
    big_frame.columnconfigure(0, weight=1)
    big_frame.rowconfigure(0, weight=1)

    info_frame = ttk.Frame(big_frame, padding=(10, 12), style="Dialog_info.TFrame")
    info_frame.grid(row=0, column=0, sticky="nsew")
    info_frame.columnconfigure(1, weight=1)
    info_frame.rowconfigure(1, weight=1)

    try:
        color = big_frame.tk.call("set", "themeColors::dialogInfoBg")
    except tk.TclError:
        color = big_frame.tk.call("ttk::style", "lookup", "TFrame", "-background")

    icon_label = ttk.Label(info_frame, image=icon, anchor="nw", background=color)
    if icon is not None:
        icon_label.grid(
            row=0, column=0, sticky="nsew", padx=(12, 0), pady=10, rowspan=2
        )

    title_label = ttk.Label(
        info_frame, text=title, anchor="nw", font=("", 24, "bold"), background=color
    )
    title_label.grid(row=0, column=1, sticky="nsew", padx=(12, 17), pady=(10, 8))

    detail_label = ttk.Label(info_frame, text=details, font=("", 15), anchor="nw", background=color)
    detail_label.grid(row=1, column=1, sticky="nsew", padx=(12, 17), pady=(5, 10))

    button_frame = ttk.Frame(
        big_frame, padding=(22, 22, 12, 22), style="Dialog_buttons.TFrame"
    )
    button_frame.grid(row=2, column=0, sticky="nsew")

    def on_button(value):
        nonlocal result
        result = value
        dialog.destroy()

    for index, button_value in enumerate(buttons):
        style = None
        state = None
        default = False
        sticky = "nes" if len(buttons) == 1 else "nsew"

        if len(button_value) > 2:
            if button_value[2] == "accent":
                style = "Accent.TButton"
                default = True
            elif button_value[2] == "disabled":
                state = "disabled"
            elif button_value[2] == "default":
                default = True

        button = ttk.Button(
            button_frame,
            text=button_value[0],
            width=18,
            command=partial(on_button, button_value[1]),
            style=style,
            state=state,
        )
        if default:
            button.bind("<Return>", button["command"])
            button.focus()

        button.grid(row=0, column=index, sticky=sticky, padx=(0, 10))

        button_frame.columnconfigure(index, weight=1)

    dialog.overrideredirect(True)
    dialog.update()

    dialog_width = dialog.winfo_width()
    dialog_height = dialog.winfo_height()

    if parent is None:
        parent_width = dialog.winfo_screenwidth()
        parent_height = dialog.winfo_screenheight()
        parent_x = 0
        parent_y = 0
    else:
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()

    x_coord = int(parent_width / 2 + parent_x - dialog_width / 2) + 250
    y_coord = int(parent_height / 2 + parent_y - dialog_height / 2) + 50

    dialog.geometry("+{}+{}".format(x_coord, y_coord))
    dialog.minsize(600, 300)

    dialog.transient(parent)
    dialog.grab_set()

    dialog.wait_window()
    return result


if __name__ == "__main__":
    window = tk.Tk()

    sv_ttk.use_light_theme()

    window.geometry("600x300")
    window.mainloop()
