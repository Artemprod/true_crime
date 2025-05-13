from cgitb import strong
from typing import Literal


from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command, Send

from src.flow.llms import llm as base_llm, character_extractor, npc_roles_extractor, npc_extractor
from src.flow.models import Character, NpcRoles, Npc
from src.flow.states import GameState, NpcRoleState
from src.prompts.characters import GENERATE_MAIN_CHARACTER_PROMPT, GENERATE_NPC_CHARACTER_PROMPT, \
    GENERATE_NPC_ROLE_PROMPT
from src.prompts.scenario import SCENARIO_PROMT, PLOT_SUMMARY_PROMPT



# Ноды


# Подграф генерации
def generatr_plot(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_main_character"]]:

    user_id = config["configurable"]['user_id']
    namespace = (user_id, "game")
    main_plot_prompt = SCENARIO_PROMT.format(n=3)
    plot = base_llm.invoke([SystemMessage(content=main_plot_prompt)])

    plot_summary_prompt = PLOT_SUMMARY_PROMPT.format(full_plot_text=plot.content,desired_summary_length="5 предложений")
    plot_summary = base_llm.invoke([SystemMessage(content=plot_summary_prompt)])

    store.put(namespace,
              key="plot",
              value={
        "plot_full":plot.content,
        "plot_summary":plot_summary.content})

    return Command(goto="generate_main_character",
                   update={"context":[plot.content] + [plot_summary.content]})


def generate_main_character(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_npc_roles"]]:

    user_id = config["configurable"]['user_id']
    namespace = (user_id, "game")
    plot = store.get(namespace, "plot") # {plot:{full, sammary}}

    main_character_prompt = GENERATE_MAIN_CHARACTER_PROMPT.format(
        plot_summary=plot.value['plot_summary'])
    response =  character_extractor.invoke(
        [SystemMessage(content=main_character_prompt)])

    character:Character = response["responses"][0]

    print(character)
    print(type(character))

    store.put(namespace,
              key="character",
              value=character.model_dump())

    return Command(goto="generate_npc_roles",
                   update={"context":[character.model_dump()]})

def generate_npc_roles(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_npc_character"]]:

    user_id = config["configurable"]['user_id']
    namespace = (user_id, "game")
    plot = store.get(namespace, "plot")

    roles_prompt = GENERATE_NPC_ROLE_PROMPT.format(n=4, plot_summary=plot.value["plot_summary"])
    response = npc_roles_extractor.invoke([SystemMessage(content=roles_prompt)])

    roles: NpcRoles = response["responses"][0]
    return Command(goto="generate_npc_character", update={"nps_roles":[role.description for role in roles.roles]})


def generate_npc_character(state: NpcRoleState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]['user_id']
    namespace = (user_id, "game")
    character = store.get(namespace, "character")
    plot = store.get(namespace, "plot")

    # Validate state has required fields
    if not state or "role" not in state:
        print("Skipping invalid NPC generation task")
        return  # Or handle this case appropriately

    print("STATE", state["role"])

    npc_prompt = GENERATE_NPC_CHARACTER_PROMPT.format(
        plot_summary=plot.value["plot_summary"],
        main_character_description=character,
        npc_role_type=state["role"])
    print()
    response= npc_extractor.invoke(
        [SystemMessage(content=npc_prompt)]
    )
    npc:Npc= response["responses"][0]
    # Проврека на существование данных в памяти
    existing_npc = store.get(namespace, "npc")

    if not existing_npc:
        store.put(namespace, "npc", value=npc.model_dump())
    else:
        existing_npc.value.update(npc.model_dump())
        store.put(namespace, "npc",existing_npc.value)

    return Command(goto="combine", update={"context":[existing_npc]})





def combine(state: GameState, config: RunnableConfig, store: BaseStore):
    return




def  generate_lavel(state: GameState, config: RunnableConfig, store: BaseStore):
    """
    Генерирует уровень на основе текущего уровня в стейте
    """



def collect_facts(state, config, store):
    """
    Взять информацию о месте
    собарь факт

    дальше либо предположить либо дальше собирать факты
    """

# Условия

def map_reduce_npc(state: GameState, config: RunnableConfig, store: BaseStore):
    return [Send("generate_npc_character", {"id": str(n), "role": r})
            for n, r in enumerate(state.get('nps_roles', []))]

def make_dicision(state, config, store):
    """
    Принимает решение сделать вывод ил дальше собирать факты
    """

# def check_conclusion(state, config, store):
#
#     if condition:
#         return Command(goto=)
#     else:
#         return Command(goto=)




