import time
import adbutils
import aircv as ac
import numpy
import random

import PathConverter

try_again = ac.imread(PathConverter.get_current_path("image\\shop_refresh_asset", "TryAgain.png"))


class Utilities:
    def __init__(self, serial: str):
        self.device = adbutils.device(serial)

    def get_numpy_screenshot(self):
        return numpy.array(self.device.screenshot())

    def find_image(self, source_img, target_img) -> dict[any, any]:
        return ac.find_template(source_img, target_img, 0.90)

    def save_image(self):
        self.device.screenshot().save("some.png")

    def swipe_down(self):
        self.device.swipe(1400, 500, 1400, 200, 0.1)

    def wait_for_button_and_click(self, target_img, description="default", timeout=5, is_multi_click = True):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_image(self.get_numpy_screenshot(), target_img):
                if is_multi_click is not True:
                    self.click_target(self.get_numpy_screenshot(), target_img, 5, False)
                else:
                    self.click_target(self.get_numpy_screenshot(), target_img)
                return True
            else:
                time.sleep(1)
        raise Exception(f"Timeout: {description} not found within {timeout} seconds")

    def wait_for_button_and_click_bool(self, target_img, description="default", timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_image(self.get_numpy_screenshot(), target_img):
                self.click_target(self.get_numpy_screenshot(), target_img)
                return True
            else:
                time.sleep(1)
        return False

    def click_center_of_screen(self):
        center_x = 500
        center_y = 500
        self.device.click(center_x, center_y)

    def click_target(self, source_img, target_img,retry_count: int = 5, is_multi_click = True, identifier: str = "default") -> bool:
        if retry_count < 0:
            print(f"Retry count less than 0, Error!")
            return False
        try:
            tup = self.find_image(source_img, target_img)
            result = tup.get("result")
            print(f"identifier: {identifier}, value: {str(tup)}")
            if is_multi_click:
                for click in range(0, random.randrange(2, 4)):
                    self.device.click(result[0], result[1])
                    time.sleep(0.2)
            else:
                self.device.click(result[0], result[1])
            return True
        except Exception as e:
            print(f"Unable to find image, Exception: {e}, identifier: {identifier}")
            is_expedition = self.check_and_refresh_expedition()
            print(f"Found expedition? {is_expedition}")
            # Re-click on target with new screenshot
            return self.click_target(self.get_numpy_screenshot(), target_img, retry_count - 1, is_multi_click, identifier)

    def check_and_refresh_expedition(self) -> bool:
        current_screenshot = self.get_numpy_screenshot()
        if self.find_image(source_img=current_screenshot, target_img=try_again):
            self.click_target(source_img=current_screenshot, target_img=try_again, identifier="refresh expedition")
            time.sleep(2)  # Wait for a bit to check if there are some other expedition coming in
            self.swipe_down()  # Need to click at least once if another expedition popping up
            return True
        return False