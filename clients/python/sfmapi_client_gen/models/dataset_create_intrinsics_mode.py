from enum import Enum


class DatasetCreateIntrinsicsMode(str, Enum):
    PER_FOLDER = "per_folder"
    PER_IMAGE = "per_image"
    SINGLE_CAMERA = "single_camera"

    def __str__(self) -> str:
        return str(self.value)
