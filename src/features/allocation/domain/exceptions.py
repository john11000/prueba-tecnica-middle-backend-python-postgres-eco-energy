"""Exceptions for the allocation domain."""
class InvalidSku(Exception):
    """Invalid sku exception is raised when a sku is not valid."""
    message = "Invalid sku {sku}"

    def __init__(self, sku: str):
        self.sku = sku

    def __str__(self):
        return self.message.format(sku=self.sku)
