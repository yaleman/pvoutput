""" Custom exceptions. """


class DonationRequiredError(Exception):
    """ A custom exception for when you call a method that requires a donation-enabled account """


class UnsupportedMethodError(Exception):
    """The specified method is not supported"""


class ConfigurationNotFoundError(Exception):
    """The configuration file could not be found"""

