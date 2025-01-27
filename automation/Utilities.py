import random
import time
from typing import Tuple

import adbutils
import cv2
import numpy
from numpy import ndarray

import PathConverter


class Utilities:
    def __init__(self, serial: str):
        self.device = adbutils.device(serial)
        print(self.device.shell('wm size'))
        screen_size = self.device.shell('wm size').split(": ")[-1]
        print(screen_size)
        self.screen_width, self.screen_height = map(int, screen_size.split("x"))
        self.is_wide_screen = self.screen_width/self.screen_height > 2
        print(f"Screen Size: {self.screen_width, self.screen_height}")
        print(f"Ratio: {self.screen_width/self.screen_height}")
        self.try_again = self.process_image_from_disk(PathConverter.get_current_path("image\\shop_refresh_asset", "TryAgain.png"))

    def get_numpy_screenshot(self):
        blur_screenshot = cv2.GaussianBlur(numpy.array(self.device.screenshot()), (5, 5), 0)
        blur_hsv_screenshot = cv2.cvtColor(blur_screenshot, cv2.COLOR_BGR2HSV)
        return blur_hsv_screenshot

    def find_image(self, source_img, target_img, confidence: float = 0.82) -> dict[any, any]:
        result = cv2.matchTemplate(source_img, target_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        print(f"confidence: {max_val}")
        if max_val >= confidence:
            top_left = max_loc
            bottom_right = (top_left[0] + target_img.shape[1], top_left[1] + target_img.shape[0])
            midpoint = int((top_left[0] + bottom_right[0])/2), int((top_left[1] + bottom_right[1])/2)
            return {"result": midpoint, "confidence": max_val}
        return {}

    def get_relative_coord(self, coord: Tuple[int, int]) -> Tuple[int, int]:
        """
        :param coord: width, height
        :return: width, height
        """

        if self.is_wide_screen:
            return int(coord[0] / 1920 * (self.screen_width * 0.8)), int(coord[1] / 1080 * self.screen_height)
        else:
            return int(coord[0] / 1920 * self.screen_width), int(coord[1] / 1080 * self.screen_height)

    def process_image_from_disk(self, path: str) -> cv2.UMat | ndarray:
        image_umat = cv2.imread(path)
        blur_umat = cv2.GaussianBlur(image_umat, (5, 5), 0)
        blur_hsv_umat = cv2.cvtColor(blur_umat, cv2.COLOR_RGB2HSV)
        height, width = blur_hsv_umat.shape[:2]
        return cv2.resize(blur_hsv_umat, self.get_relative_coord((width, height)), interpolation=cv2.INTER_LINEAR_EXACT)

    def save_image(self, save_file_name: str = "some.png"):
        self.device.screenshot().save(save_file_name)

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

    def click_by_position(self, target_img=None, future_target_img=None, position_offset=(0, 0), retry_count: int = 3,
                          identifier: str = "default") -> bool:
        if retry_count < 0:
            print(f"Retry count less than 0, Error!")
            return False
        try:
            source_img = self.get_numpy_screenshot()
            target_img_pos = self.find_image(source_img, target_img)

            if bool(target_img_pos):
                print(f"identifier: {identifier}, img value: {str(target_img_pos)}")
                result = target_img_pos.get("result")
                relative_position_offset = self.get_relative_coord(position_offset)
                click_position = (result[0] + relative_position_offset[0], result[1] + relative_position_offset[1])
                self.device.click(click_position[0], click_position[1])
                # Check if it actually clicked if future_target_img is provided
                if future_target_img is not None:
                    # Wait for animation
                    time.sleep(0.5)
                    print("looking for future target img")
                    future_img_result = self.find_image(self.get_numpy_screenshot(), future_target_img)
                    print(f"future img result: {future_img_result}")
                    if not bool(future_img_result):
                        print("future image not found, trying again")
                        return self.click_by_position(target_img, future_target_img, position_offset, retry_count - 1, identifier)
                return True
        except Exception as e:
            print(f"Unable to find image, Exception: {e}, identifier: {identifier}")
            is_expedition = self.check_and_refresh_expedition()
            print(f"Found expedition? {is_expedition}")
            # Re-click on target with new screenshot
            return self.click_by_position(target_img, future_target_img, position_offset, retry_count - 1, identifier)

    def better_click_target(self, target_img=None, future_target_img=None, retry_count: int = 3,
                            identifier: str = "default") -> bool:
        if retry_count < 0:
            print(f"Retry count less than 0, Error!")
            return False
        try:
            source_img = self.get_numpy_screenshot()
            target_img_pos = self.find_image(source_img, target_img)
            if bool(target_img_pos):
                print(f"identifier: {identifier}, img value: {str(target_img_pos)}")
                result = target_img_pos.get("result")
                self.device.click(result[0], result[1])
                # Check if it actually clicked if future_target_img is provided
                if future_target_img is not None:
                    # Wait for animation
                    time.sleep(0.5)
                    print("looking for future target img")
                    future_img_result = self.find_image(self.get_numpy_screenshot(), future_target_img)
                    print(f"future img result: {future_img_result}")
                    if not bool(future_img_result):
                        print("future image not found, trying again")
                        return self.better_click_target(target_img, future_target_img, retry_count - 1, identifier)
                return True
            if future_target_img is not None:
                print("looking for future target img 2")
                if self.find_image(source_img, future_target_img):
                    return True
            raise ValueError("Cannot Find Image")
        except Exception as e:
            print(f"Unable to find image, Exception: {e}, identifier: {identifier}")
            is_expedition = self.check_and_refresh_expedition()
            print(f"Found expedition? {is_expedition}")
            # Re-click on target with new screenshot
            return self.better_click_target(target_img, future_target_img, retry_count - 1, identifier)

    def check_and_refresh_expedition(self) -> bool:
        current_screenshot = self.get_numpy_screenshot()
        if self.find_image(source_img=current_screenshot, target_img=self.try_again):
            self.better_click_target(target_img=self.try_again, identifier="refresh expedition")
            time.sleep(2)  # Wait for a bit to check if there are some other expedition coming in
            self.swipe_down()  # Need to click at least once if another expedition popping up
            return True
        return False
