import tkinter as tk
import threading

class TranslationOverlay:
    def __init__(self, opacity: float = 0.9, font_size: int = 12, auto_hide: int = 5, position: str = "right-bottom"):
        self.auto_hide = auto_hide
        self.position = position
        self._hide_timer = None
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", opacity)
        self.root.configure(bg="#1e1e1e")

        self.label = tk.Label(
            self.root, text="", wraplength=400, justify="left",
            bg="#1e1e1e", fg="#d4d4d4", font=("微软雅黑", font_size), padx=10, pady=8
        )
        self.label.pack()

        # 拖动支持
        self.root.bind("<ButtonPress-1>", self._drag_start)
        self.root.bind("<B1-Motion>", self._drag_move)
        self.root.bind("<Double-Button-1>", lambda e: self.root.withdraw())

        self._place_window()
        self.root.withdraw()

    def _place_window(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = sw - 450 if "right" in self.position else 10
        y = sh - 120 if "bottom" in self.position else 10
        self.root.geometry(f"+{x}+{y}")

    def _drag_start(self, e):
        self._dx, self._dy = e.x, e.y

    def _drag_move(self, e):
        x = self.root.winfo_x() + e.x - self._dx
        y = self.root.winfo_y() + e.y - self._dy
        self.root.geometry(f"+{x}+{y}")

    def show(self, original: str, translated: str):
        def _update():
            self.label.config(text=f"EN: {original[:80]}{'...' if len(original)>80 else ''}\n中: {translated}")
            self.root.deiconify()
            self.root.update()
            if self.auto_hide > 0:
                if self._hide_timer:
                    self._hide_timer.cancel()
                self._hide_timer = threading.Timer(self.auto_hide, self.root.withdraw)
                self._hide_timer.start()
        self.root.after(0, _update)

    def run(self):
        self.root.mainloop()
