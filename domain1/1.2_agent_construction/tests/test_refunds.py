from refunds import refund_amount


def test_damaged_within_14_days():
    assert refund_amount(289, 10, True) == 289


def test_change_of_mind_within_30_days():
    assert refund_amount(499, 21, False) == 499


def test_day_30_still_qualifies():
    assert refund_amount(499, 30, False) == 499


def test_after_30_days():
    assert refund_amount(499, 31, False) == 0
