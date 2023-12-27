class BaseError(Exception):
    """Base Exception error class."""
    def __init__(self):
        super().__init__()

class DiskNotFoundError(BaseError):
    """Raised when a disk was not found."""
    def __init__(self, dev_path):
        self.message = f"Disk {dev_path} not found."
        super().__init__()