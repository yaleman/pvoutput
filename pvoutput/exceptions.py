""" Custom exceptions. """


class DonationRequired(Exception):
    """A custom exception for when you call a method that requires a donation-enabled account"""


class UnknownMethodError(Exception):
    """The method is unknown."""
