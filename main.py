#run game graph
import os
from langgraph.checkpoint.redis import RedisSaver
from langgraph.constants import START

from src.flow.nodes import generatr_plot, generate_main_character, generate_npc_character, map_reduce_npc, \
    generate_npc_roles, combine
from langgraph.graph import StateGraph
from langgraph.store.postgres import PostgresStore
from src.flow.states import GameState
from dotenv import load_dotenv

load_dotenv()

builder = StateGraph(GameState)
builder.add_node("generatr_plot",generatr_plot)
builder.add_node("generate_main_character",generate_main_character)
builder.add_node("generate_npc_roles",generate_npc_roles)
builder.add_node("generate_npc_character",generate_npc_character)
builder.add_node("combine",combine)

builder.set_entry_point("generatr_plot")
builder.add_conditional_edges("generate_npc_roles",map_reduce_npc, ["generate_npc_character"] )
builder.set_finish_point("combine")


with (
    PostgresStore.from_conn_string(os.environ.get("POSTGRES_DATABASE_URL")) as store,
    RedisSaver.from_conn_string(os.environ.get("REDIS_DB_URI")) as checkpointer,
):
    # store.setup()
    # checkpointer.setup()

    graph = builder.compile(checkpointer=checkpointer, store=store)

    config = {"configurable": {"thread_id": "thread_7", "user_id":"2"}}

    stream = graph.stream({}, config=config, debug=True)
    for event in stream:
        print(event)

