class ObjectClickResult:
    def __init__(self, object_found: bool, click_success: bool):
        self.object_found = object_found
        self.click_success = click_success
