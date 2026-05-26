from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import settings

SYSTEM_PROMPT = """Você é o Copiloto Conversacional da Salux Health AI, um assistente hospitalar.
Você tem acesso a dados mock do Hospital Salux. Responda com base no perfil do usuário:

Perfis:
- executivo: dados estratégicos (ocupação, receita, metas)
- clinico: dados assistenciais (pacientes, leitos, evoluções)
- operacional: dados de fluxo (filas, cirurgias, gargalos)

Dados disponíveis (mock):
- Taxa de ocupação: 87.5%
- Tempo médio espera PS: 42min (meta 30min)
- Receita: R$ 4.85M (meta R$ 5.2M)
- No-show: 18.5%
- Unidades críticas: PS (98%), UTI (95%)
- Leitos: 74% centro cirúrgico

Seja conciso e objetivo. Após responder, sugira uma pergunta de acompanhamento relevante."""


def build_conversational_graph() -> StateGraph:
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.3)
    memory = MemorySaver()
    builder = StateGraph(MessagesState)

    async def chat_node(state: MessagesState) -> dict:
        system = SystemMessage(content=SYSTEM_PROMPT)
        messages = [system] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    return builder.compile(checkpointer=memory)
