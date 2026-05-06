from enum import Enum


class GlobalSpecBackend(str, Enum):
    AUTO = "AUTO"
    BAXX = "BAXX"
    CERES = "CERES"

    def __str__(self) -> str:
        return str(self.value)
