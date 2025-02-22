import multiprocessing
import sys

from ui.DeviceSelection import DeviceSelectionUI
import customtkinter as tk


# This class acts as holder
class RootWindow(tk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    root_window = RootWindow()
    DeviceSelectionUI(root_window)
    root_window.mainloop()
