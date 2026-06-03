import tkinter as tk
import customtkinter as ctk
import ctypes
import threading
import json
import os
import sys
from urllib.request import urlopen, Request


def _config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "calculator_config.json")
    return os.path.join(os.path.dirname(__file__), "calculator_config.json")


def _read_config(key, default):
    try:
        with open(_config_path()) as f:
            return json.load(f).get(key, default)
    except Exception:
        return default


def _is_newer(remote, current):
    try:
        r = tuple(int(x) for x in remote.split("."))
        c = tuple(int(x) for x in current.split("."))
        return r > c
    except Exception:
        return False


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Taschenrechner")
        self.root.geometry("340x480")
        self.root.resizable(False, False)

        self.root.overrideredirect(True)

        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x40000)

        self.expression = ""
        self.new_number = True
        self._start_x = 0
        self._start_y = 0

        self._build_ui()

    def _build_ui(self):
        window_card = ctk.CTkFrame(self.root, fg_color="#181825", corner_radius=24, border_width=1, border_color="#252538")
        window_card.pack(fill=tk.BOTH, expand=True)

        title_bar = ctk.CTkFrame(window_card, fg_color="transparent", height=40)
        title_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        title_bar.pack_propagate(False)

        title_bar.bind("<Button-1>", self._on_press)
        title_bar.bind("<B1-Motion>", self._on_drag)

        close_btn = ctk.CTkButton(title_bar, text="×", font=("Segoe UI", 18),
                                  fg_color="transparent", text_color="#6c7086", hover_color="#f38ba8",
                                  width=28, height=28, corner_radius=8, command=self._on_close)
        close_btn.pack(side=tk.RIGHT, padx=5)

        title_mini = ctk.CTkLabel(title_bar, text="Taschenrechner", font=("Segoe UI", 12, "bold"), text_color="#585b70")
        title_mini.pack(side=tk.LEFT, padx=10)
        title_mini.bind("<Button-1>", self._on_press)
        title_mini.bind("<B1-Motion>", self._on_drag)

        container = ctk.CTkFrame(window_card, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        title_label = ctk.CTkLabel(container, text="Taschenrechner", font=("Segoe UI", 22, "bold"), text_color="#ffffff")
        title_label.pack(pady=(5, 15))

        self.display_var = tk.StringVar(value="0")
        self.display = ctk.CTkEntry(
            container,
            textvariable=self.display_var,
            font=("Segoe UI", 28, "bold"),
            justify="right",
            fg_color="#1e1e2e",
            border_color="#313244",
            text_color="#cdd6f4",
            corner_radius=12,
            height=60,
            state="readonly"
        )
        self.display.pack(fill=tk.X, pady=(0, 15))

        button_grid = ctk.CTkFrame(container, fg_color="transparent")
        button_grid.pack(fill=tk.BOTH, expand=True)

        buttons = [
            ("C", "#313244", "#f38ba8", 1, 0, 1, 1),
            ("±", "#313244", "#cdd6f4", 1, 1, 1, 1),
            ("%", "#313244", "#cdd6f4", 1, 2, 1, 1),
            ("÷", "#ff8c00", "#ffffff", 1, 3, 1, 1),
            ("7", "#3c3c4a", "#cdd6f4", 2, 0, 1, 1),
            ("8", "#3c3c4a", "#cdd6f4", 2, 1, 1, 1),
            ("9", "#3c3c4a", "#cdd6f4", 2, 2, 1, 1),
            ("×", "#ff8c00", "#ffffff", 2, 3, 1, 1),
            ("4", "#3c3c4a", "#cdd6f4", 3, 0, 1, 1),
            ("5", "#3c3c4a", "#cdd6f4", 3, 1, 1, 1),
            ("6", "#3c3c4a", "#cdd6f4", 3, 2, 1, 1),
            ("−", "#ff8c00", "#ffffff", 3, 3, 1, 1),
            ("1", "#3c3c4a", "#cdd6f4", 4, 0, 1, 1),
            ("2", "#3c3c4a", "#cdd6f4", 4, 1, 1, 1),
            ("3", "#3c3c4a", "#cdd6f4", 4, 2, 1, 1),
            ("+", "#ff8c00", "#ffffff", 4, 3, 1, 1),
            ("0", "#3c3c4a", "#cdd6f4", 5, 0, 2, 1),
            (",", "#3c3c4a", "#cdd6f4", 5, 2, 1, 1),
            ("=", "#89b4fa", "#11111b", 5, 3, 1, 1),
        ]

        button_grid.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="btn")
        button_grid.grid_rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="btn")

        for text, bg, fg, row, col, colspan, rowspan in buttons:
            btn = ctk.CTkButton(
                button_grid,
                text=text,
                font=("Segoe UI", 18, "bold"),
                fg_color=bg,
                text_color=fg,
                hover_color=self._hover_color(bg),
                corner_radius=10,
                height=52,
                command=lambda t=text: self._button_click(t)
            )
            btn.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan,
                     sticky="nsew", padx=3, pady=3)

        update_frame = ctk.CTkFrame(container, fg_color="transparent")
        update_frame.pack(fill=tk.X, pady=(12, 0))

        self.update_btn = ctk.CTkButton(update_frame, text="Nach Updates suchen", font=("Segoe UI", 11, "bold"),
                                        fg_color="#313244", text_color="#cdd6f4", hover_color="#45475a",
                                        height=28, corner_radius=6, command=self._check_update)
        self.update_btn.pack(side=tk.LEFT, padx=2)

        self.update_label = ctk.CTkLabel(update_frame, text="", font=("Segoe UI", 11), text_color="#6c7086")
        self.update_label.pack(side=tk.LEFT, padx=(8, 0))

        self.root.bind("<Key>", self._key_press)

        threading.Thread(target=self._check_update_silent, daemon=True).start()

    def _hover_color(self, color):
        if color == "#313244":
            return "#45475a"
        if color == "#3c3c4a":
            return "#50506a"
        if color == "#ff8c00":
            return "#e07b00"
        if color == "#89b4fa":
            return "#74a8f0"
        return color

    def _on_press(self, event):
        self._start_x = event.x
        self._start_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._start_x + event.x
        y = self.root.winfo_y() - self._start_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def _button_click(self, text):
        if text == "C":
            self.expression = ""
            self.display_var.set("0")
            self.new_number = True
        elif text == "=":
            try:
                result = self._evaluate(self.expression)
                self.display_var.set(self._format_number(result))
                self.expression = str(result)
                self.new_number = True
            except Exception:
                self.display_var.set("Error")
                self.expression = ""
                self.new_number = True
        elif text == "±":
            if self.display_var.get() not in ("0", "Error"):
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format_number(-val))
                self.expression = self.display_var.get().replace(".", ",")
        elif text == "%":
            try:
                val = float(self.display_var.get().replace(",", "."))
                self.display_var.set(self._format_number(val / 100))
                self.expression = self.display_var.get().replace(".", ",")
            except Exception:
                self.display_var.set("Error")
                self.expression = ""
                self.new_number = True
        else:
            if self.new_number:
                self.expression = ""
                self.new_number = False

            if text in ("÷", "×", "−", "+"):
                op_map = {"÷": "/", "×": "*", "−": "-", "+": "+"}
                self.expression += op_map[text]
            elif text == ",":
                last_num = self.expression
                for sep in "+-*/":
                    if sep in last_num:
                        last_num = last_num.rsplit(sep, 1)[-1]
                if "." in last_num:
                    return
                self.expression += "."
            else:
                self.expression += text

            display_text = self.expression.replace(".", ",")
            self.display_var.set(display_text)

    def _evaluate(self, expr):
        expr = expr.replace(",", ".")
        result = eval(expr)
        return result

    def _format_number(self, num):
        if isinstance(num, float) and num == int(num):
            return str(int(num)).replace(".", ",")
        return str(num).replace(".", ",")

    def _key_press(self, event):
        key = event.char
        if key in "0123456789":
            self._button_click(key)
        elif key == ",":
            self._button_click(",")
        elif key == ".":
            self._button_click(",")
        elif key in "+-*/":
            op_map = {"+": "+", "-": "−", "*": "×", "/": "÷"}
            self._button_click(op_map[key])
        elif key == "\r":
            self._button_click("=")
        elif key == "\x08":
            self._button_click("C")

    def _check_update_silent(self):
        threading.Event().wait(3)
        try:
            self._do_check(silent=True)
        except Exception:
            pass

    def _check_update(self):
        self.update_label.configure(text="Suche...", text_color="#6c7086")
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self, silent=False):
        url = _read_config("update_url", "")
        ver = _read_config("version", "1.0")
        try:
            req = Request(url, headers={"User-Agent": "Calculator/1.0"})
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            remote = data.get("version", "")
            installer_url = data.get("installer_url", "")

            if not remote or not installer_url:
                return

            if _is_newer(remote, ver):
                self.root.after(0, lambda: self._ask_update(remote, installer_url))
            elif not silent:
                self.root.after(0, lambda: self.update_label.configure(
                    text=f"v{ver} ist aktuell", text_color="#a6e3a1"))
        except Exception:
            if not silent:
                self.root.after(0, lambda: self.update_label.configure(
                    text="Offline", text_color="#f38ba8"))

    def _ask_update(self, version, installer_url):
        from tkinter import messagebox
        app_ver = _read_config("version", "1.0")
        if messagebox.askyesno(
            "Update verfügbar",
            f"Version {version} ist verfügbar.\n"
            f"Aktuelle Version: {app_ver}\n\n"
            "Die App wird geschlossen und der Download gestartet."
        ):
            self._download_and_close(installer_url)

    def _download_and_close(self, url):
        from tkinter import messagebox
        self.root.withdraw()
        import tempfile
        import subprocess
        try:
            path = os.path.join(tempfile.gettempdir(), "Taschenrechner_Update_Setup.exe")
            req = Request(url, headers={"User-Agent": "Calculator/1.0"})
            with urlopen(req, timeout=120) as resp:
                with open(path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            subprocess.Popen(
                [path, "/SP-", "/NORESTART"],
                creationflags=subprocess.DETACHED_PROCESS,
                close_fds=True
            )
        except Exception:
            messagebox.showerror("Fehler", "Download fehlgeschlagen.")
        finally:
            self.root.destroy()

    def _on_close(self):
        self.root.destroy()


def main():
    root = ctk.CTk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
