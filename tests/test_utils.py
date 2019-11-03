from utils import duration_to_int


def test_duration_to_int():
    duration = "28 min"
    assert duration_to_int(duration) == 28

    duration = "2 h 08 min"
    assert duration_to_int(duration) == 2 * 60 + 8

    duration = "3 h"
    assert duration_to_int(duration) == 3 * 60
