from loguru import logger
from langgraph.types import interrupt, Command
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Literal

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


# Ноды
def generate_level(state, config, store):
    """
    Генерирует уровень на основе текущего уровня в стейте
    :param state:
    :param config:
    :param store:
    :return:
    """
    ...


def collect_facts(state, config, store):
    ...


# Условия
def check_conclusion(state, config, store):
    ...
