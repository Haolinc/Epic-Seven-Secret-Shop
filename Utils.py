import random
import time
import numpy
import adbutils
import aircv as ac

from ObjectClickResult import ObjectClickResult
import PathConverter

covenant = ac.imread(PathConverter.get_current_path("image", "Covenant.png"))
covenant_buy = ac.imread(PathConverter.get_current_path("image", "CovenantBuy.png"))
covenant_buy_confirmation = ac.imread(PathConverter.get_current_path("image", "CovenantBuyConfirmation.png"))
mystic = ac.imread(PathConverter.get_current_path("image", "Mystic.png"))
mystic_buy = ac.imread(PathConverter.get_current_path("image", "MysticBuy.png"))
mystic_buy_confirmation = ac.imread(PathConverter.get_current_path("image", "MysticBuyConfirmation.png"))
refresh = ac.imread(PathConverter.get_current_path("image", "Refresh.png"))
refresh_confirm = ac.imread(PathConverter.get_current_path("image", "RefreshConfirm.png"))
try_again = ac.imread(PathConverter.get_current_path("image", "TryAgain.png"))


class Utils:
    def __init__(self, serial: str):
        self.device = adbutils.device(serial)

    def __get_numpy_screenshot(self):
        return numpy.array(self.device.screenshot())

    def __find_image(self, source_img, target_img) -> dict[any, any]:
        return ac.find_template(source_img, target_img, 0.95)

    def __click_target(self, source_img, target_img, identifier: str = "default", retry_count: int = 2) -> bool:
        if retry_count < 0:
            print(f"Retry count less than 0, Error!")
            return False
        try:
            tup = self.__find_image(source_img, target_img)
            result = tup.get("result")
            print(f"identifier: {identifier}, value: {str(tup)}")
            for click in range(0, random.randrange(2, 4)):
                self.device.click(result[0], result[1])
                time.sleep(0.2)
            return True
        except Exception as e:
            print(f"Unable to find image, Exception: {e}")
            is_expedition = self.__refresh_expedition()
            print(f"Found expedition? {is_expedition}")
            self.__click_target(source_img, target_img, identifier, retry_count - 1)

    def __refresh_expedition(self) -> bool:
        current_screenshot = self.device.screenshot()
        if self.__find_image(source_img=current_screenshot, target_img=try_again):
            self.__click_target(source_img=current_screenshot, target_img=try_again, identifier="refresh expedition")
            return True
        return False

    def swipe_down(self):
        self.device.swipe(900, 500, 900, 0)

    def check_covenant(self) -> bool:
        return self.__find_image(source_img=self.__get_numpy_screenshot(), target_img=covenant) is not None

    def buy_covenant(self) -> bool:
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=covenant_buy,
                                   identifier="buy covenant in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=covenant_buy_confirmation,
                                   identifier="buy covenant in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def check_mystic(self) -> bool:
        return self.__find_image(source_img=self.__get_numpy_screenshot(), target_img=mystic) is not None

    def buy_mystic(self) -> bool:
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=mystic_buy,
                                   identifier="buy mystic in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=mystic_buy_confirmation,
                                   identifier="buy mystic in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def refresh_shop(self) -> bool:
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=refresh,
                                   identifier="refresh in store page"):
            return False
        time.sleep(0.2)  # Delay is for animation
        if not self.__click_target(source_img=self.__get_numpy_screenshot(), target_img=refresh_confirm,
                                   identifier="refresh in confirmation page"):
            return False
        time.sleep(0.2)
        return True

    def check_and_buy_covenant(self) -> ObjectClickResult:
        if self.check_covenant():
            return ObjectClickResult(object_found=True, click_success=self.buy_covenant())
        return ObjectClickResult(object_found=False, click_success=True)

    def check_and_buy_mystic(self) -> ObjectClickResult:
        if self.check_mystic():
            return ObjectClickResult(object_found=True, click_success=self.buy_mystic())
        return ObjectClickResult(object_found=False, click_success=True)
