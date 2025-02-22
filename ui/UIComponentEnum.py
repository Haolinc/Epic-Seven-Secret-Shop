from enum import Enum, auto


class LabelEnum(Enum):
    COVENANT_COUNT = 'covenant_count_label'
    MYSTIC_COUNT = 'mystic_count_label'
    TOP = 'top_label'
    ARENA = 'arena_label'


class ButtonEnum(Enum):
    SHOP_REFRESH_START = 'start_shop_refresh_button'
    ARENA_START = 'start_arena_button'


class EntryEnum(Enum):
    SHOP_REFRESH_COUNT_ENTRY = 'refresh_shop_count_entry'
    ARENA_COUNT_ENTRY = 'arena_count_entry'


class CheckBoxEnum(Enum):
    ARENA_WITH_FRIENDSHIP = 'arena_with_extra'


class UIComponent(Enum):
    SHOP_REFRESH = auto()
    ARENA = auto()
    ALL = auto()


class UIThreadMessage(Enum):
    ADD_TO_LOG_FRAME = auto()
    START_SHOP_REFRESH = auto()
    START_DAILY_ARENA = auto()
    STOP = auto()
    COVENANT_FOUND = auto()
    MYSTIC_FOUND = auto()
    RESET_LOG = auto()
    ERROR = auto()
