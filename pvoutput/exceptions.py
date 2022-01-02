""" Custom exceptions. """


class DonationRequired(Exception):
    """A custom exception for when you call a method that requires a donation-enabled account"""


class UnknownMethodError(Exception):
    """The method is unknown."""


class InvalidRegexpError(Exception):
    """There was an error with the regexp format for this key"""


class UnknownAlertTypeError(Exception):
    """The provided Alert Type is not supported"""
