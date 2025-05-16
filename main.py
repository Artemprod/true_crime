#run game graph
import os
from langgraph.checkpoint.redis import RedisSaver
from langgraph.constants import START


from langgraph.graph import StateGraph
from langgraph.store.postgres import PostgresStore

from src.flow.nodes import introduction
from src.flow.states import GameState
from dotenv import load_dotenv

from src.flow.subgraphs.game_creation.graph import game_creation_builder

load_dotenv()

builder = StateGraph(GameState)


builder.add_node("create_game",game_creation_builder.compile)
builder.add_node("introduction",introduction)

builder.set_entry_point("create_game")
builder.set_finish_point("introduction")


with (
    PostgresStore.from_conn_string(os.environ.get("POSTGRES_DATABASE_URL")) as store,
    RedisSaver.from_conn_string(os.environ.get("REDIS_DB_URI")) as checkpointer,
):
    # store.setup()
    # checkpointer.setup()
    print()
    graph = builder.compile(checkpointer=checkpointer, store=store)


    config = {
        "configurable": {"thread_id": "thread_17", "user_id":"2"},
         "metadata":{"locations":2,"npc":2}
        }

    stream = graph.stream({}, config=config, debug=False)
    for event in stream:
        print(event)


    print()
