
from langgraph.graph import StateGraph



from dotenv import load_dotenv

from src.flow.states import GameState
from src.flow.subgraphs.game_creation.nodes import clear_memory, generatr_plot, generate_main_character, \
    generate_npc_roles, generate_npc_character, generate_level, map_reduce_npc, map_reduce_level

load_dotenv()

game_creation_builder = StateGraph(GameState)
game_creation_builder.add_node("clear_memory",clear_memory)
game_creation_builder.add_node("generatr_plot",generatr_plot)
game_creation_builder.add_node("generate_main_character",generate_main_character)
game_creation_builder.add_node("generate_npc_roles",generate_npc_roles)
game_creation_builder.add_node("generate_npc_character",generate_npc_character)
game_creation_builder.add_node("generate_level",generate_level)


game_creation_builder.set_entry_point("generatr_plot")
game_creation_builder.add_conditional_edges("generate_npc_roles",map_reduce_npc, ["generate_npc_character"] )
game_creation_builder.add_conditional_edges("generate_npc_character",map_reduce_level, ["generate_level"] )
game_creation_builder.set_finish_point("generate_level")



