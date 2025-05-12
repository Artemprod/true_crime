from pprint import pprint
from langgraph.types import interrupt, Command
from loguru import logger
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Literal

from langchain_openai import ChatOpenAI
from research_planer.states import GraphState
from dotenv import load_dotenv

# Ноды
def  generate_lavel(state, config, store):
    """
    Генерирует уровень на основе текущего уровня в стейте
    :param state:
    :param config:
    :param store:
    :return:
    """
    ...

def collec_facts(state, config, store):
    ...

# Условия
def check_conclusion(state, config, store)->:
    if condition:
        return Command(goto=)
    else:
        return Command(goto=)

while True
    graph.invoke()
    graph.update_ste()


