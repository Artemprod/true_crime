import operator
from typing import Annotated

from langgraph.graph import MessagesState
from research_planer.models import ResearchPlan
from typing_extensions import TypedDict

class GameState(TypedDict):
    context:Annotated[str, operator.add]
    current_level:str # Подгрузка из памяти
    next_level:str
    is_allow:bool # можно попробовать разрешать проход на сл цуровне флагом


