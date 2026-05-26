from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.config import settings
from src.db import get_kpi_text, get_hospital_units

BASE_SYSTEM_PROMPT = """You are the Personal AI Conversational Copilot, an intelligent assistant.
You have access to live hospital data. Answer based on the user profile:

Profiles:
- executive: strategic data (occupancy, revenue, goals)
- clinical: care data (patients, beds, progress notes)
- operational: flow data (queues, surgeries, bottlenecks)

Be concise and objective. After answering, suggest a relevant follow-up question."""


async def chat_node(state: MessagesState) -> dict:
    kpis = await get_kpi_text()
    units = await get_hospital_units()
    unit_lines = []
    for u in units:
        unit_lines.append(f"- {u['nome']}: {u['ocupacao']}% occupancy, {u['espera_min']}min wait, status {u['status']}")
    units_str = "\n".join(unit_lines) if unit_lines else "No unit data available."

    context = (
        f"Current hospital data:\n\n"
        f"KPIs:\n{kpis}\n\n"
        f"Units:\n{units_str}"
    )

    llm = ChatOpenAI(model=settings.openai_model, temperature=0.3)
    system = SystemMessage(content=f"{BASE_SYSTEM_PROMPT}\n\n{context}")
    messages = [system] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


def build_conversational_graph() -> StateGraph:
    memory = MemorySaver()
    builder = StateGraph(MessagesState)

    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    return builder.compile(checkpointer=memory)
