import json
from typing import Literal, Optional
from uuid import uuid4

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command, Send

from src.flow.llms import llm as base_llm, character_extractor, npc_roles_extractor, npc_extractor, location_extractor
from src.flow.models import Character, NpcRoles, Npc
from src.flow.states import GameState, NpcRoleState, LevelState
from src.prompts.characters import GENERATE_MAIN_CHARACTER_PROMPT, GENERATE_NPC_CHARACTER_PROMPT, \
    GENERATE_NPC_ROLE_PROMPT
from src.prompts.level import GENERATE_LOCATION_PROMPT
from src.prompts.scenario import SCENARIO_PROMT, PLOT_SUMMARY_PROMPT, INTRODUCTION_SUMMARY_PROMPT
# Ноды
# Подграф генерации
def clear_memory(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generatr_plot"]]:

    user_id = config["configurable"]['user_id']

    npc = store.search((user_id, "npc"))
    game = store.search((user_id, "game"))
    locations = store.search((user_id, "locations"))

    if npc:
        for i in npc:
            store.delete((user_id, "npc"), i.key)

    if game:
        for i in game:
            store.delete((user_id, "game"), i.key)

    if locations:
        for i in locations:
            store.delete((user_id, "locations"), i.key)

    print("Memory cleared")
    return Command(goto="generatr_plot")


def generatr_plot(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_main_character"]]:

    user_id = config["configurable"]['user_id']
    locations_num = config["metadata"]['locations']
    namespace = (user_id, "game")

    main_plot_prompt = SCENARIO_PROMT.format(n=locations_num)
    plot = base_llm.invoke([SystemMessage(content=main_plot_prompt)])

    plot_summary_prompt = PLOT_SUMMARY_PROMPT.format(full_plot_text=plot.content, desired_summary_length="5 предложений")
    plot_summary = base_llm.invoke([SystemMessage(content=plot_summary_prompt)])

    store.put(namespace,
              key="plot",
              value={
        "plot_full":plot.content,
        "plot_summary":plot_summary.content})

    return Command(goto="generate_main_character")

def generate_main_character(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_npc_roles"]]:

    user_id = config["configurable"]['user_id']
    namespace = (user_id, "game")
    plot = store.get(namespace, "plot") # {plot:{full, sammary}}

    main_character_prompt = GENERATE_MAIN_CHARACTER_PROMPT.format(
        plot_summary=plot.value['plot_summary'])
    response =  character_extractor.invoke(
        [SystemMessage(content=main_character_prompt)])

    character:Character = response["responses"][0]
    store.put(namespace,
              key="character",
              value=character.model_dump())

    return Command(goto="generate_npc_roles")

def generate_npc_roles(state: GameState, config: RunnableConfig, store: BaseStore)-> Command[Literal["generate_npc_character"]]:

    user_id = config["configurable"]['user_id']
    npc_num = config["metadata"]['npc']
    namespace = (user_id, "game")
    plot = store.get(namespace, "plot")

    roles_prompt = GENERATE_NPC_ROLE_PROMPT.format(n=npc_num, plot_summary=plot.value["plot_summary"])
    response = npc_roles_extractor.invoke([SystemMessage(content=roles_prompt)])

    roles: NpcRoles = response["responses"][0]
    return Command(goto="generate_npc_character", update={"nps_roles":[role.description for role in roles.roles]})

def generate_npc_character(state: NpcRoleState, config: RunnableConfig, store: BaseStore)-> Optional[Command[Literal["generate_level"]]]:
    user_id = config["configurable"]['user_id']
    character = store.get((user_id, "game"), "character")
    plot = store.get((user_id, "game"), "plot")

    # Validate state has required fields
    if not state or "role" not in state:
        print("Skipping invalid NPC generation task")
        return  # Or handle this case appropriately

    npc_prompt = GENERATE_NPC_CHARACTER_PROMPT.format(
        plot_summary=plot.value["plot_summary"],
        main_character_description=character,
        npc_role_type=state["role"])

    response= npc_extractor.invoke(
        [SystemMessage(content=npc_prompt)]
    )
    npc:Npc = response["responses"][0]

    store.put((user_id, "npc"), str(uuid4()), value=npc.model_dump())
    return Command(goto="generate_level",)

def generate_level(state: LevelState, config: RunnableConfig, store: BaseStore)-> Optional[Command[Literal[END]]]:

    if not state or "number" not in state:
        print("Skipping invalid Level generation task")
        return  # Or handle this case appropriately

    user_id = config["configurable"]['user_id']
    level_number = state["number"]

    plot = (store.get((user_id, "game"), "plot")).value['plot_full']
    npc_list = ";\n".join([json.dumps(npc.value,ensure_ascii=False ) for npc in store.search((user_id, "npc"))])

    level_generation_prompt = GENERATE_LOCATION_PROMPT.format(full_plot_text=plot,
                                                              all_npcs_list=npc_list,
                                                              level_number=level_number,)

    response = location_extractor.invoke(
        [SystemMessage(content=level_generation_prompt)]
    )
    location = response["responses"][0]
    store.put((user_id, "locations"), key=str(level_number), value=location.model_dump())
    return Command(goto=END)
#Условия
def map_reduce_npc(state: GameState, config: RunnableConfig, store: BaseStore):
    return [Send("generate_npc_character", {"id": str(n), "role": r})
            for n, r in enumerate(state.get('nps_roles', []))]

def map_reduce_level(state: GameState, config: RunnableConfig, store: BaseStore):
    locations_num = config["metadata"]['locations']
    return [Send("generate_level", {"number":n }) for n in range(1, locations_num+1)]