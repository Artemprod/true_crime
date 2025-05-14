from langgraph.checkpoint.redis import RedisSaver
from langgraph.types import Command
from loguru import logger
from langgraph.graph import StateGraph, MessagesState, END
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from dotenv import load_dotenv

_ = load_dotenv()

llm = ChatMistralAI(model="mistral-large-latest", temperature=0.2)
lllm = ChatOpenAI(model="gp")


class AgentState(MessagesState):
    user_id: int
    answer: str
    question: str
    node: str


class CheckAnswerOutput(BaseModel):
    correct: bool


def first_question(state: AgentState):
    logger.info("Node: first_question")
    response = llm.invoke(
        [
            SystemMessage(
                "Придумай простую математическую задачу, например 2 + 2 без ответа"
            )
        ]
    )
    return {
        "question": response.content,
        "node": "first_question",
        "messages": [response],
    }


def second_question(state: AgentState):
    logger.info("Node: second_question")
    response = llm.invoke(
        [
            SystemMessage(
                "Придумай другую простую математическую задачу на подобии 2 + 2"
            )
        ]
    )
    return {
        "question": response.content,
        "node": "second_question",
        "messages": [response],
    }


def third_question(state: AgentState):
    logger.info("Node: third_question")
    response = llm.invoke(
        [SystemMessage("Придумай еще одну простую математическую задачу")]
    )
    return {
        "question": response.content,
        "node": "third_question",
        "messages": [response],
    }


def check_answer(state: AgentState):
    logger.info(
        f"Checking answer: {state.get('answer', 'не знаю ответ')} for question: {state['question']}"
    )
    response = llm.with_structured_output(CheckAnswerOutput).invoke(
        [
            SystemMessage(
                content=f"Проверь решение пользователя на задание: {state['question']}"
            ),
            HumanMessage(content=state.get("answer", "не знаю ответ")),
        ]
    )
    logger.info(f"Answer correct: {response.correct}")

    updates = {"is_correct": response.correct}

    next_steps = {
        "first_question": "second_question",
        "second_question": "third_question",
        "third_question": END,
    }
    if not response.correct:
        logger.info(f"Answer is incorrect, from node {state['node']} -> (ask_again)")
        "ask_again"

    return next_steps[state.get("node", "first_question")]


def ask_again(state: AgentState):
    logger.info("Asking the same question again")
    response = llm.invoke(
        [
            SystemMessage(
                content=f"Попроси пользователя ответить на этот вопрос {state['question']}"
            )
        ]
    )
    return Command(goto=state.get("node"), update={"messages": [response]})


# Создаем граф
graph = StateGraph(AgentState)
graph.add_node("first_question", first_question)
graph.add_node("second_question", second_question)
graph.add_node("third_question", third_question)
graph.add_node("ask_again", ask_again)

graph.set_entry_point("first_question")

graph.add_conditional_edges(
    "first_question",
    check_answer,
    ["ask_again", "second_question", ],
)
graph.add_conditional_edges(
    "second_question",
    check_answer,
    ["third_question", "ask_again"],
)

graph.add_conditional_edges(
    "third_question",
    check_answer,
    ["ask_again", END],
)

# app = graph.compile(interrupt_after=["first_question", "second_question", "third_question"])

with RedisSaver.from_conn_string("redis://localhost:6378/0") as checkpointer:
    checkpointer.setup()
    app = graph.compile(
        interrupt_after=["first_question", "second_question", "third_question"],
        checkpointer=checkpointer
    )

    thread = {"configurable": {"thread_id": "22k"}}
    initial_state = {"user_id": 1, "messages": []}
    while True:
        interrupt_found = False
        for event in app.stream({}, thread, stream_mode="updates"):
            if "__interrupt__" in event:
                interrupt_found = True
                state = app.get_state(thread)
                if state.values["messages"]:
                    print(state.values["messages"][-1].content)
                else:
                    print(state.values["question"])
                user_input = input(">>> ")
                app.update_state(
                    thread,
                    {
                        "answer": user_input,
                        "messages": state.values["messages"]
                                    + [HumanMessage(content=user_input)],
                    }
                )
        if not interrupt_found:
            print("Все вопросы завершены!")
            break
        initial_state = {}  # Сбрасываем для следующей итерации
