import operator
from typing import Annotated, List

from typing_extensions import TypedDict

class GameState(TypedDict):

    context:Annotated[List[str], operator.add]
    current_level:int
    is_allow: bool # можно попробовать разрешать проход на сл цуровне флагом
    nps_roles:List[str]


class NpcRoleState(TypedDict):
    id:str
    role:str

class LevelState(TypedDict):
    number:int