"""Refund amounts under Acme policy 1.1 and 2.1, used by fix_tests.py: the agent finds and fixes the bug the tests catch."""


def refund_amount(price, days_since_delivery, damaged):
    """Price refunded for a return: damaged items reported within 14 days of delivery, change of mind within 30 days."""
    if damaged and days_since_delivery <= 14:
        return price
    if days_since_delivery < 30:
        return price
    return 0
