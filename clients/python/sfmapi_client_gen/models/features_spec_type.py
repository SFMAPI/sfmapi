from enum import Enum


class FeaturesSpecType(str, Enum):
    ALIKED = "aliked"
    D2NET = "d2net"
    DISK = "disk"
    R2D2 = "r2d2"
    SIFT = "sift"
    SUPERPOINT = "superpoint"

    def __str__(self) -> str:
        return str(self.value)
