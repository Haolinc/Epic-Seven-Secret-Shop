import threading
import time

import aircv as ac
import PathConverter
from automation.Utilities import Utilities
from ui.UIComponentEnum import *

covenant = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "Covenant.png"))
covenant_buy = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "CovenantBuy.png"))
covenant_buy_confirmation = ac.imread(
    PathConverter.get_current_path("image\\shop_refresh_asset", "CovenantBuyConfirmation.png"))
mystic = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "Mystic.png"))
mystic_buy = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "MysticBuy.png"))
mystic_buy_confirmation = ac.imread(
    PathConverter.get_current_path("image\\shop_refresh_asset", "MysticBuyConfirmation.png"))
refresh = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "Refresh.png"))
refresh_confirm = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "RefreshConfirm.png"))


class ShopRefresh:
    thread_shutdown = threading.Event()

    def __init__(self, utilities: Utilities, listener):
        self.utilities = utilities
        self.covenant_count = 0
        self.mystic_count = 0
        self.ui_listener = listener

    def check_covenant(self) -> bool:
        return self.utilities.find_image(source_img=self.utilities.get_numpy_screenshot(),
                                         target_img=covenant) is not None

    def buy_covenant(self) -> bool:
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=covenant_buy,
                                                 identifier="buy covenant in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=covenant_buy_confirmation,
                                                 identifier="buy covenant in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def check_mystic(self) -> bool:
        return self.utilities.find_image(source_img=self.utilities.get_numpy_screenshot(),
                                         target_img=mystic) is not None

    def buy_mystic(self) -> bool:
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=mystic_buy,
                                                 identifier="buy mystic in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=mystic_buy_confirmation,
                                                 identifier="buy mystic in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def refresh_shop(self) -> bool:
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=refresh,
                                                 identifier="refresh in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.utilities.click_target(source_img=self.utilities.get_numpy_screenshot(),
                                                 target_img=refresh_confirm,
                                                 identifier="refresh in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def check_bookmark_and_update_log(self):
        if self.check_covenant():
            if self.buy_covenant():
                self.ui_listener.add_label_to_log_frame(text="Found Covenant Bookmark!")
                self.covenant_count += 5
                self.ui_listener.set_label_text(label_enum=LabelEnum.COVENANT_COUNT,
                                                text="Total Covenant: " + str(self.covenant_count))
            # This only happens when multiple retry attempt fails
            else:
                self.ui_listener.add_label_to_log_frame(text="Covenant Purchase Fail, Stopping the application")
                self.stop_shop_refresh()
                return
        if self.check_mystic():
            if self.buy_mystic():
                self.ui_listener.add_label_to_log_frame(text="Found Mystic Bookmark!")
                self.mystic_count += 50
                self.ui_listener.set_label_text(label_enum=LabelEnum.MYSTIC_COUNT,
                                                text="Total Mystic: " + str(self.mystic_count))
            # This only happens when multiple retry attempt fails
            else:
                self.ui_listener.add_label_to_log_frame(text="Mystic Purchase Fail, Stopping the application")
                self.stop_shop_refresh()

    def start_store_fresh_iteration(self):
        total_iteration: int = self.ui_listener.get_entry_count(EntryEnum.SHOP_REFRESH_COUNT_ENTRY)
        current_iteration = 1
        self.ui_listener.reset_log_frame()
        while current_iteration <= total_iteration and not self.thread_shutdown.is_set():
            self.ui_listener.add_label_to_log_frame(text=f"--------Iteration: {current_iteration}--------")
            self.check_bookmark_and_update_log()
            if self.thread_shutdown.is_set():
                break
            self.utilities.swipe_down()
            time.sleep(0.5)
            self.check_bookmark_and_update_log()
            # Check shutdown signal before refresh
            if self.thread_shutdown.is_set():
                break
            # When refresh failed, Stop the application
            if not self.refresh_shop():
                self.ui_listener.add_label_to_log_frame(text="Refresh Shop Fail, Stopping the application")
                break
            current_iteration += 1
        # Check again for last refresh ONLY when thread is not exiting
        if not self.thread_shutdown.is_set():
            self.check_bookmark_and_update_log()
            self.utilities.swipe_down()
            time.sleep(0.5)
            self.check_bookmark_and_update_log()
        self.ui_listener.add_label_to_log_frame(text="####### Process Stopped #######")
        self.ui_listener.reset_ui_component(UIComponent.SHOP_REFRESH)

    def start_shop_refresh_with_thread(self):
        self.thread_shutdown.clear()
        threading.Thread(target=self.start_store_fresh_iteration, daemon=True).start()

    def stop_shop_refresh(self):
        self.thread_shutdown.set()

