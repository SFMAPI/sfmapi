from enum import Enum


class PairsSpecRetrievalStrategy(str, Enum):
    DHASH = "dhash"
    NETVLAD = "netvlad"
    VLAD = "vlad"

    def __str__(self) -> str:
        return str(self.value)
