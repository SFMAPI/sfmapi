from enum import Enum


class UploadOutState(str, Enum):
    EXPIRED = "expired"
    FINALIZED = "finalized"
    OPEN = "open"
    RECEIVED = "received"

    def __str__(self) -> str:
        return str(self.value)
