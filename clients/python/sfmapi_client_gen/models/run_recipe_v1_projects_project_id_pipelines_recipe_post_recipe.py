from enum import Enum


class RunRecipeV1ProjectsProjectIdPipelinesRecipePostRecipe(str, Enum):
    GLOBAL = "global"
    HIERARCHICAL = "hierarchical"
    INCREMENTAL = "incremental"
    SPHERICAL = "spherical"

    def __str__(self) -> str:
        return str(self.value)
