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
    location: str = Field(..., description="Название и номер локации на которой находится персонаж исходя из общей сюжетной линии")
    description: str= Field(..., description="внешний вид, особенности поведения")
    personality: Optional[str] = None  # черты характера, напр: 'жесткий', 'доброжелательный'
    mood: Optional[str] = "neutral"  # текущее настроение NPC
    known_facts: List[str] = []  # что NPC знает
    inventory: Optional[List[str]] = []  # предметы у NPC
    hostility: Optional[int] = 0  # уровень враждебности от 0 до 100
    trust_level: Optional[int] = 50  # степень доверия к игроку (0–100)

class LocationObject(BaseModel):
    name: str = Field(..., description="Уникальное название интерактивного объекта на локации (например, 'Старинный сейф', 'Письменный стол детектива').")
    description: str = Field(..., description="Краткое визуальное описание объекта: как он выглядит, его состояние, ключевые внешние черты.")
    details: Optional[str] = Field(None, description="Более подробная информация, которую можно получить при тщательном осмотре объекта, или его скрытые особенности (например, 'Нацарапанная надпись на дне ящика', 'Тайный отсек под крышкой').")
    plot_clues: List[str] = Field(default_factory=list, description="Список ключевых фактов, улик или сюжетной информации, которые можно получить/обнаружить при взаимодействии с этим объектом. Эти улики должны помогать решать загадку уровня.")
    approximate_location: Optional[str] = Field(None, description="Примерное расположение объекта на игровой локации (например, 'В дальнем правом углу комнаты', 'На каминной полке', 'Под кроватью').")

class Location(BaseModel):
    number: int = Field(..., description="Порядковый номер уровня или локации в общей сюжетной линии.")
    description: str = Field(..., description="Атмосферное и общее описание локации, передающее ее ключевые визуальные и сенсорные характеристики, а также общее настроение.")
    objects: List[LocationObject] = Field(default_factory=list, description="Список ключевых интерактивных объектов, находящихся на данной локации.")
    npc: List[str] = Field(default_factory=list, description="Список имен NPC (персонажей, не управляемых игроком), которые присутствуют на этой локации и с которыми можно взаимодействовать.")
    facts: List[str] = Field(default_factory=list, description="Список агрегированных ключевых фактов, улик и наблюдений, доступных на локации. Эти факты должны быть достаточны для решения загадки уровня и могут быть получены из объектов, от NPC или через прямое наблюдение.")
    goal: str = Field(..., description="Одна четкая и однозначная цель, которую Главный Герой должен достичь на этом уровне для продвижения по сюжету.")
    riddle: str = Field(..., description="Одна конкретная и недвусмысленная загадка или вопрос, который Главный Герой должен решить на этом уровне, чтобы достичь поставленной цели.")
    correct_answer: str = Field(..., description="Один точный и логически вытекающий из 'facts' правильный ответ на 'riddle', решение которого приводит к достижению 'goal'.")


class Game(BaseModel):
    character:Character
    main_goal:str
    history:str
    locations: Optional[list[Location]]






