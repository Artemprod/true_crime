from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    name:str
    game_played:str

class Conclusion(BaseModel):
    text:str

class Fact(BaseModel):
    location:str
    source: str
    text:str


class Character(BaseModel):
    name:str
    bio:str
    gathered_facts:str
    conclusions:List[Conclusion]


class Npc(BaseModel):
    name: str
    role: str
    description: str  # внешний вид, особенности поведения
    personality: Optional[str] = None  # черты характера, напр: 'жесткий', 'доброжелательный'
    mood: Optional[str] = "neutral"  # текущее настроение NPC
    known_facts: List[str] = []  # что NPC знает
    inventory: Optional[List[str]] = []  # предметы у NPC
    hostility: Optional[int] = 0  # уровень враждебности от 0 до 100
    trust_level: Optional[int] = 50  # степень доверия к игроку (0–100)


class Location(BaseModel):
    facts:List[str]
    description:str
    goal:str
    riddle:str
    npc:List[Npc]


class Game(BaseModel):
    locations:List[Location]





