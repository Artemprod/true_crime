import json


from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command, Send
from numpy.distutils.system_info import system_info
from scripts.regsetup import description
from win32comext.adsi.demos.scp import logger

from src.flow.llms import llm as base_llm, character_extractor, npc_roles_extractor, npc_extractor, location_extractor, \
    fact_extractor, conclusion_extractor, correct_extractor
from src.flow.models import Character, NpcRoles, Npc, Location
from src.flow.states import GameState, NpcRoleState, LevelState
from src.prompts.actions import INSPECT_LOCATION_PROMPT, GET_FACT_PROMPT, CHECK_CONCLUSION_PROMPT, MAKE_CONCLUSION
from src.prompts.characters import GENERATE_MAIN_CHARACTER_PROMPT, GENERATE_NPC_CHARACTER_PROMPT, \
    GENERATE_NPC_ROLE_PROMPT
from src.prompts.level import GENERATE_LOCATION_PROMPT, LEVEL_DESCRIPTION_PROMPT
from src.prompts.scenario import SCENARIO_PROMT, PLOT_SUMMARY_PROMPT, INTRODUCTION_SUMMARY_PROMPT, CONCLUSION_PROMPT


convert_to_text = lambda memory_object:"\n".join(f"{key}:{value}" for key, value in memory_object.value.items())

def introduction(state: GameState, config: RunnableConfig, store: BaseStore):
    logger.debug("INTRODUCTION")
    user_id = config["configurable"]['user_id']


    full_plot_text =  (store.get((user_id, "game"), "plot")).value["plot_full"]
    character_db = (store.get((user_id, "game"), "character"))
    main_character_description = convert_to_text(character_db)

    introduction_prompt = INTRODUCTION_SUMMARY_PROMPT.format(full_plot_text=full_plot_text,
                                                            main_character_description=main_character_description,)

    introduction_response = base_llm.invoke([SystemMessage(content=introduction_prompt)])

    go_further = interrupt(
        "Идем на первую локацию?  (да/нет)"
    )

    if go_further.lower() == "да":
        return Command(goto="generate_leval_description",
                       update={"context":[introduction_response.content],
                               "current_level":1,
                                "is_allow":True,
                               })




def generate_leval_description(state: GameState, config: RunnableConfig, store: BaseStore):
    """
    Генерирует уровень на основе текущего уровня в стейте
    """
    logger.debug("GEN LEVEL")
    current_level = state["current_level"]
    user_id = config["configurable"]['user_id']
    current_location = store.get((user_id, "locations"), key=str(current_level),)
    character_db = store.get((user_id, "game"), "character")
    character = convert_to_text(character_db)
    level_description_prompt = LEVEL_DESCRIPTION_PROMPT.format(main_character_description=character, current_level_data=current_location, )
    description = base_llm.invoke([SystemMessage(content=level_description_prompt)])
    store.put((user_id, "game"), "level_description", value={"description":description.content})
    return Command(goto="collect_facts", update={"context":[description.content]})



def collect_facts(state: GameState, config: RunnableConfig, store: BaseStore):
    """
    Взять информацию о месте
    собарь факт

    дальше либо предположить либо дальше собирать факты
    """
    logger.debug("COLLECT FACTS")
    answer = interrupt(
        "Что ты делаешь?"
    )
    current_level = state["current_level"]
    user_id = config["configurable"]['user_id']
    levl_descr = (store.get((user_id, "game"), key="level_description")).value['description']
    level_facts= convert_to_text(store.get((user_id, "locations"), key=str(current_level)))

    fact_prompt = INSPECT_LOCATION_PROMPT.format(user_action=answer,level_description=levl_descr,level_facts=level_facts)
    action_description = base_llm.invoke([SystemMessage(content=fact_prompt)])
    get_fact_response = fact_extractor.invoke(GET_FACT_PROMPT.format(source_text=action_description.content))
    fact = get_fact_response["response"][0]
    existing_facts = [f for f in store.search((user_id, 'facts')) if f.key.startswith(f"{current_level}")]
    store.put((user_id, 'facts'), key=f"{current_level}_{len(existing_facts) + 1}", value=fact.model_dump())
    return Command(goto="make_decision", update={'context':[action_description.content]})


def make_decision(state: GameState, config: RunnableConfig, store: BaseStore):
    """
    Принимает решение сделать вывод ил дальше собирать факты
    """

    current_level = state["current_level"]
    user_id = config["configurable"]['user_id']
    existing_facts = [fact.value for fact in store.search((user_id, 'facts')) if fact.key.startswith(str(current_level))]
    answer = interrupt(
       f"Теперь у тебя есть такие факты: {existing_facts } какой твой ответ? "
    )
    level_facts = store.get((user_id, "locations"), key=str(current_level))
    location = Location(**level_facts.dict())

    conclusion_response = conclusion_extractor.invoke(MAKE_CONCLUSION.format(user_response=answer))
    conclusion=conclusion_response["response"][0]

    correct_response = correct_extractor.invoke(
        CHECK_CONCLUSION_PROMPT.format(
            correct_riddle_answer=location.correct_answer,
            player_answer=conclusion,))
    correct = correct_response["response"][0]

    existing_conclusion = [c for c in store.search((user_id, 'conclusions')) if c.key.startswith(f"{current_level}")]
    store.put((user_id, "conclusions"),key=f"{current_level}_{len(existing_conclusion) + 1}",
              value={"conclusion":conclusion, "is_correct":correct})

    if answer is not correct:
        return Command(goto="collect_facts")

    if answer is correct and current_level < config["metadata"]['locations'] :
        return Command(goto="generate_leval_description", update={"current_level":current_level + 1})

    elif answer is correct and current_level == config["metadata"]['locations']:
        return Command(goto="conclusion")

    else:
        ...

def conclusion(state: GameState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]['user_id']
    full_plot_text =  (store.get((user_id, "game"), "plot")).value["plot_full"]
    main_character_description = convert_to_text(store.get((user_id, "game"), "character"))

    facts = ";\n".join([json.dumps(f.value) for f in store.search((user_id, 'facts'))])
    player_conclusions =  ";\n".join([json.dumps(f.value) for f in  store.search((user_id, 'conclusions'))])

    conclusion_prompt = CONCLUSION_PROMPT.format(main_character_description=main_character_description,
                                                   full_plot_summary=full_plot_text,
                                                   all_collected_facts=facts,
                                                   key_player_conclusions=player_conclusions)

    conclusion_response = base_llm.invoke([SystemMessage(content=conclusion_prompt)])
    return Command(goto=END, update={"context":[conclusion_response.content]})



