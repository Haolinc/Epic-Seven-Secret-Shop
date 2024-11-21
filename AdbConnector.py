import subprocess
import PathConverter
import PIL.Image as Image
import adbutils

# Must call refresh_adb_device_list to update the dictionary before using
serial_and_image_dict: dict[str, Image.Image] = {}


# TODO: try 5 second scan once to fetch new device in background thread
def refresh_adb_device_list():
    serial_and_image_dict.clear()
    adb_command = PathConverter.get_current_path("platform-tools", "adb devices -l")
    adb_device_result_list = subprocess.run(adb_command, capture_output=True, text=True).stdout.splitlines()
    adb_device_result_list.pop(0)
    adb_device_result_list.pop()
    for adb_device_info in adb_device_result_list:
        lst = adb_device_info.split(" ")  # lst[0] is the serial number
        serial_name = lst[0]
        current_model_device = adbutils.device(lst[0])
        current_device_image: Image = current_model_device.screenshot()
        serial_and_image_dict[serial_name] = current_device_image
