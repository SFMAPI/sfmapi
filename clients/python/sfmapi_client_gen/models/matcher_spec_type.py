from enum import Enum


class MatcherSpecType(str, Enum):
    LIGHTGLUE = "lightglue"
    LOFTR = "loftr"
    MAST3R = "mast3r"
    NN_MUTUAL = "nn-mutual"
    NN_RATIO = "nn-ratio"
    SUPERGLUE = "superglue"

    def __str__(self) -> str:
        return str(self.value)
