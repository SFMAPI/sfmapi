from enum import Enum


class GlobalSpecFormulation(str, Enum):
    AUTO = "AUTO"
    ELIMINATED_SCALE = "ELIMINATED_SCALE"
    EXPLICIT_SCALE = "EXPLICIT_SCALE"

    def __str__(self) -> str:
        return str(self.value)
