from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from trustcall import create_extractor

from src.flow.models import Character, NpcRoles, Npc, Location, Fact, Conclusion, CorrectAnswer

load_dotenv()
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=1)


character_extractor = create_extractor(
    llm=llm,
    tools=[Character],
    tool_choice="Character",
    enable_inserts=True
)

npc_extractor = create_extractor(
    llm=llm,
    tools=[Npc],
    tool_choice="Npc",
    enable_inserts=True
)

npc_roles_extractor = create_extractor(
    llm=llm,
    tools=[NpcRoles],
    tool_choice="NpcRoles",
    enable_inserts=True
)


location_extractor = create_extractor(
    llm=llm,
    tools=[Location],
    tool_choice="Location",
    enable_inserts=True
)

fact_extractor = create_extractor(
    llm=llm,
    tools=[Fact],
    tool_choice="Fact",
    enable_inserts=True
)
conclusion_extractor = create_extractor(
    llm=llm,
    tools=[Conclusion],
    tool_choice="Conclusion",
    enable_inserts=True
)

correct_extractor = create_extractor(
    llm=llm,
    tools=[CorrectAnswer],
    tool_choice="CorrectAnswer",
    enable_inserts=True
)
