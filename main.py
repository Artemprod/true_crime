#run game graph
import os
from langgraph.checkpoint.redis import RedisSaver
from langgraph.constants import START


from langgraph.graph import StateGraph
from langgraph.store.postgres import PostgresStore
from langgraph.types import Command
from loguru import logger

from src.flow.nodes import introduction, generate_leval_description, collect_facts, make_decision, conclusion
from src.flow.states import GameState
from dotenv import load_dotenv

from src.flow.subgraphs.game_creation.graph import game_creation_builder

load_dotenv()

builder = StateGraph(GameState)


builder.add_node("create_game",game_creation_builder.compile)

builder.add_node("introduction",introduction)
builder.add_node("generate_leval_description",generate_leval_description)
builder.add_node("collect_facts",collect_facts)
builder.add_node("make_decision",make_decision)
builder.add_node("conclusion",conclusion)


builder.set_entry_point("create_game")
builder.add_edge("create_game","introduction" )
builder.set_finish_point("conclusion")





with (
    PostgresStore.from_conn_string(os.environ.get("POSTGRES_DATABASE_URL")) as store,
    RedisSaver.from_conn_string(os.environ.get("REDIS_DB_URI")) as checkpointer,
):
    store.setup()
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer, store=store)


    config = {
        "configurable": {"thread_id": "thread_4994900", "user_id":"2"},
         "metadata":{"locations":2,"npc":2}
        }

    state = {}
    is_continue = True

    while is_continue:
        stream = graph.stream(state, config, stream_mode="updates")

        for event in stream:
            current_graph_state = graph.get_state(config)
            logger.debug(f"СОСТОЯНИЕ  {current_graph_state}")
            logger.debug(f"CСЛЕДУЮщее  {current_graph_state.next}")


            if not current_graph_state.next:  # Если state.next пустой (граф завершился)
                print("Граф завершил выполнение.")
                is_continue = False
                break

            # Если это interrupt, ждём ввод пользователя
            if "__interrupt__" in event:
                interrupt_data = event["__interrupt__"][0]
                print(interrupt_data.value)
                user_input = input(">>> ")
                # передаём ответ пользователя как resume
                state = Command(resume=user_input)
                break
            else:
                # если event обычный — обновляем состояние
                state = None
