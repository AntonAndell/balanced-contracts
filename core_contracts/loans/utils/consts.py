from iconservice import *

DEFAULT_CAP_VALUE = 2 ** 256 -1
DEFAULT_DECIMAL_VALUE = 18
ZERO_SCORE_ADDRESS = "cxf000000000000000000000000000000000000000"
EXA = 1000000000000000000
U_SECONDS_DAY = 86400000000  # Microseconds in a day.
DEFAULT_MINING_RATIO = 500
DEFAULT_LOCKING_RATIO = 400
DEFAULT_LIQUIDATION_RATIO = 125
MIN_UPDATE_TIME = 30000000  # 30 seconds
POINTS = 10000
LIQUIDATION_REWARD = 67 # Points of collateral sent to liquidator as a reward.
REPLAY_BATCH_SIZE = 100
DEFAULT_ORIGINATION_FEE = 100
DEFAULT_REDEMPTION_FEE = 50
BAD_DEBT_RETIREMENT_BONUS = 1000

POSITION_DB_PREFIX = b'position'

def get_day_index(loans) -> int:
    return (loans.now() // U_SECONDS_DAY) % 2


class Standing:
    LIQUIDATE = 0
    LOCKED = 1
    NOT_MINING = 2
    MINING = 3
    UNDETERMINED = 4
    STANDINGS = ['Liquidate', 'Locked', 'Not Mining', 'Mining', 'Undetermined']
