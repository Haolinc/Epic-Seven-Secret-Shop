import multiprocessing

import customtkinter as tk

import ui.UIHelper as UIHelper
from automation.DailyArena import DailyArena
from automation.ShopRefresh import ShopRefresh
from automation.Utilities import Utilities
from ui.ProcessManager import ProcessManager
from ui.UIComponentEnum import *

tk.set_appearance_mode("System")


class MainWindow(tk.CTkToplevel):
    """
    Main window for automation.
    """
    def __init__(self, root, utilities: Utilities):
        super().__init__(root)
        self.log_frame = None
        self.refresh_shop_count_entry = None
        self.arena_count_entry = None
        self.arena_checkbox = None
        self.arena_with_extra = None
        self.top_label = None
        self.mystic_count_label = None
        self.covenant_count_label = None
        self.msg_queue = multiprocessing.Queue()
        self.shop_refresh = ShopRefresh(utilities, self.msg_queue)
        self.shop_refresh_process = None
        self.daily_arena = DailyArena(utilities, self.msg_queue)
        self.daily_arena_process = None

        self.title("E7 Secret Shop Auto")
        self.geometry("500x630")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.__create_main_widgets()
        self.ui_listener = Listener(self)
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        UIHelper.set_window_icon(self)

    def __create_main_widgets(self):
        # Main frame setup
        main_frame = tk.CTkFrame(self)
        main_frame.grid(pady=15, padx=15, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Top frame with counters
        top_count_frame = tk.CTkFrame(main_frame)
        top_count_frame.grid(pady=(10, 5), padx=10, sticky="ew")
        top_count_frame.grid_columnconfigure((0, 1), weight=1)  # Equal spacing for labels

        # Covenant and Mystic count labels
        self.covenant_count_label = tk.CTkLabel(top_count_frame, text="Total Covenant: 0", anchor="w")
        self.covenant_count_label.grid(pady=5, padx=(10, 5), column=0, row=0, sticky="ew")
        self.mystic_count_label = tk.CTkLabel(top_count_frame, text="Total Mystic: 0", anchor="e")
        self.mystic_count_label.grid(pady=5, padx=(5, 10), column=1, row=0, sticky="ew")

        # Label and input for iterations
        self.top_label = tk.CTkLabel(main_frame, text="Enter Total Iterations", anchor="w")
        self.top_label.grid(pady=(10, 5), padx=10, sticky="ew")
        self.refresh_shop_count_entry = tk.CTkEntry(main_frame, placeholder_text="Refresh Count")
        self.refresh_shop_count_entry.grid(pady=5, padx=10, sticky="ew")

        # Start button
        self.start_shop_refresh_button = tk.CTkButton(main_frame, text="Start Shop Refresh",
                                                      command=self.__run_shop_refresh_process)
        self.start_shop_refresh_button.grid(pady=(5, 15), padx=10, sticky="ew")

        # Arena options
        arena_label = tk.CTkLabel(main_frame, text="Arena Settings", anchor="w", font=("Arial", 12, "bold"))
        arena_label.grid(pady=(10, 5), padx=10, sticky="w")

        self.arena_count_entry = tk.CTkEntry(main_frame, placeholder_text="Arena Count")
        self.arena_count_entry.grid(pady=5, padx=10, sticky="ew")
        self.arena_with_extra = tk.BooleanVar(value=False)
        self.arena_checkbox = tk.CTkCheckBox(
            main_frame,
            text="Arena with Extra",
            variable=self.arena_with_extra,
            onvalue=True,
            offvalue=False
        )
        self.arena_checkbox.grid(pady=5, padx=10, sticky="w")

        # Arena start button
        self.start_arena_button = tk.CTkButton(main_frame, text="Start Arena", command=self.__run_arena_process)
        self.start_arena_button.grid(pady=(5, 15), padx=10, sticky="ew")

        # Logger frame to track log
        self.log_frame = tk.CTkScrollableFrame(master=main_frame, height=250, width=500)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid(padx=10, sticky="nsew")

    def __run_shop_refresh_process(self):
        """
        To run or terminate secret shop process.
        """
        if self.start_shop_refresh_button.cget("text") == "Start Shop Refresh":
            self.shop_refresh_process = ProcessManager(function=self.shop_refresh.start_store_fresh_iteration,
                                                       args=(int(self.refresh_shop_count_entry.get()),),
                                                       ui_listener=self.ui_listener,
                                                       msg_queue=self.msg_queue)
            self.shop_refresh_process.start_process()
        else:
            self.start_shop_refresh_button.configure(state="disabled")
            UIHelper.add_label_to_frame(frame=self.log_frame, text="####### Process Stopping, Please Wait #######")
            self.shop_refresh_process.stop_process()

    def __run_arena_process(self):
        """
        To run or terminate NPC challenge arena process.
        """
        total_iteration: int = self.ui_listener.get_entry_count(EntryEnum.ARENA_COUNT_ENTRY)
        run_with_friendship_flag: bool = self.ui_listener.get_checkbox_bool(CheckBoxEnum.ARENA_WITH_FRIENDSHIP)

        if self.start_arena_button.cget("text") == "Start Arena":
            self.start_arena_button.configure(text="Stop Arena Automation")
            self.daily_arena_process = ProcessManager(function=self.daily_arena.run_arena_automation_subprocess,
                                                      args=(total_iteration, run_with_friendship_flag),
                                                      ui_listener=self.ui_listener,
                                                      msg_queue=self.msg_queue)
            self.daily_arena_process.start_process()
        else:
            self.start_arena_button.configure(state="disabled")
            UIHelper.add_label_to_frame(frame=self.log_frame,
                                        text="####### Process Stopping, Please Wait #######")
            self.daily_arena_process.stop_process()


class Listener:
    """
    Class that allow other classes to manipulate UI elements.
    """
    def __init__(self, parent: MainWindow):
        self.parent = parent

    def add_label_to_log_frame(self, text: str):
        UIHelper.add_label_to_frame(frame=self.parent.log_frame, text=text)

    def reset_log_frame(self):
        UIHelper.reset_frame(frame=self.parent.log_frame)

    def set_label_text(self, label_enum: LabelEnum, text: str):
        self.parent.__getattribute__(label_enum.value).configure(text=text)

    def get_label_text(self, label_enum: LabelEnum) -> str:
        return str(self.parent.__getattribute__(label_enum.value).cget("text"))

    def set_button_text(self, button_enum: ButtonEnum, text: str):
        self.parent.__getattribute__(button_enum.value).configure(text=text)

    def set_button_state(self, button_enum: ButtonEnum, state: str):
        self.parent.__getattribute__(button_enum.value).configure(state=state)

    def reset_ui_component(self):
        self.parent.start_shop_refresh_button.configure(state="normal")
        self.parent.start_shop_refresh_button.configure(text="Start Shop Refresh")
        self.parent.start_arena_button.configure(state="normal")
        self.parent.start_arena_button.configure(text="Start Arena")

    def get_entry_count(self, entry_enum: EntryEnum) -> int:
        return int(self.parent.__getattribute__(entry_enum.value).get())

    def get_checkbox_bool(self, check_box_enum: CheckBoxEnum) -> bool:
        return bool(self.parent.__getattribute__(check_box_enum.value).get())
