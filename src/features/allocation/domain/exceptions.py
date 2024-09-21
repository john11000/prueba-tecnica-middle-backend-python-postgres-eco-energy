"""Exceptions for the domain."""

class InvalidValueError(Exception):
    """Invalid value exption is raised when has no found the db record."""
    message = "Error: {msg}"

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.message.format(msg=self.msg)
class InvalidSku(Exception):
    """Invalid sku exception is raised when a sku is not valid."""
    message = "Invalid sku {sku}"

    def __init__(self, sku: str):
        self.sku = sku

    def __str__(self):
        return self.message.format(sku=self.sku)
