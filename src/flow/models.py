from typing import List, Optional, Dict

from pydantic import BaseModel, Field

class Fact(BaseModel):
    location:str
    source: str
    text:str

class Conclusion(BaseModel):
    text:str

class User(BaseModel):
    name:str
    gathered_facts:List[Fact]
    conclusions: List[Conclusion]


class Character(BaseModel):
    name: str = Field(..., description="Имя главного героя")
    bio: str = Field(..., description="Краткая биография персонажа, описывающая его историю и роль в сюжете")
    birth_place: Optional[str] = Field(None, description="Место рождения персонажа")
    birth_date: Optional[str] = Field(None, description="Дата рождения персонажа (формат YYYY-MM-DD)")
    appearance: Optional[str] = Field(None, description="Описание внешности персонажа")
    personality_traits: List[str] = Field(default_factory=list, description="Основные черты характера персонажа")
    motivations: Optional[str] = Field(None, description="Главная мотивация персонажа, движущая его поступками")
    fears: List[str] = Field(default_factory=list, description="Страхи и фобии персонажа")
    goals: Optional[str] = Field(None, description="Ключевые цели и задачи персонажа в истории")
    skills: List[str] = Field(default_factory=list, description="Ключевые навыки и умения персонажа")
    flaws: List[str] = Field(default_factory=list, description="Недостатки и слабости персонажа")
    character_arc: Optional[str] = Field(
        None,
        description="Эволюция персонажа на протяжении истории: как и почему он изменяется"
    )


class NpcRole(BaseModel):
    description:str = Field(..., description='Краткое описание требуемой роли или типа NPC в сюжете '
                                             '(например, "Свидетель ключевого события на первой локации", '
                                             '"Потенциальный информатор, работающий в баре на второй локации", '
                                             '"Мелкий преступник, который может обладать нужной уликой",'
                                             ' "Эксперт, к которому Главный Герой обращается за консультацией")')

class NpcRoles(BaseModel):
    roles:List[NpcRole]


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
    correct_answer:str
    npc:List[Npc]


class Game(BaseModel):
    character:Character
    main_goal:str
    history:str
    locations: Optional[list[Location]]






