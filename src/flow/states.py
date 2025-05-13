import operator
from typing import Annotated, List

from typing_extensions import TypedDict

class GameState(TypedDict):
    context:Annotated[List[str], operator.add]
    current_level:str # Подгрузка из памяти
    next_level:str
    is_allow:bool # можно попробовать разрешать проход на сл цуровне флагом
    nps_roles:List[str]

class NpcRoleState(TypedDict):
    id:str
    role:str

