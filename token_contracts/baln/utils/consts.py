DEFAULT_DECIMAL_VALUE = 18
DEFAULT_INITIAL_SUPPLY = 0
DAY_TO_MICROSECOND = 864 * 10 ** 8


class Status:
    AVAILABLE = 0
    STAKED = 1
    UNSTAKING = 2
    UNSTAKING_PERIOD = 3


MAX_LOOP = 100
INITIAL_PRICE_ESTIMATE = 10**17
MIN_UPDATE_TIME = 2000000 # 2 seconds
DEFAULT_UNSTAKING_PERIOD = 3 * DAY_TO_MICROSECOND
