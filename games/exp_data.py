import math

# Curves: https://i.imgur.com/7ZjUtpQ.png

# From levels 1-5, we use a generous curve.
# From 5-infinity, we use an exponential curve of 1.87 (and then an offset to ensure it starts at level 5).

# https://www.desmos.com/calculator/jjiph0tvqr - EXP from LEVEL
# https://www.desmos.com/calculator/aqynsvx9pg - LEVEL from EXP

# Inverse of get exp from level functions
def get_exact_level(exp):
    if exp < 200:
        # Level 1 = 0, Level 5 = 192
        ret = math.sqrt((exp + 8) / 8)
    else:
        ret = math.sqrt((exp - 142) / 2)
    if ret < 1.00:
        ret = 1 # Level 1 is the minimum

    return ret

def get_rounded_level(exp):
    return int(math.floor(get_exact_level(exp)))