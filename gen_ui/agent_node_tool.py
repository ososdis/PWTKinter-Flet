import json
import logging
from typing import Annotated, List, Literal, Optional

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from msgpack import os
from pydantic import BaseModel, Field

os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"


def setup_llm_model(base_url: str, api_key: str, model_name: str | None):
    """Fonction appelée par Flet pour initialiser l'IA avec vos choix d'écran."""
    global llm
    os.environ["OPENAI_API_KEY"] = api_key
    if model_name:
        llm = ChatOpenAI(base_url=base_url, model=model_name, temperature=0.3)
    os.environ["OPENAI_BASE_URL"] = base_url


# --- DÉFINITION DES TOOLS LANGCHAIN ---


@tool
def fetch_live_weather(city: str) -> str:
    """Consulte les conditions météorologiques actuelles pour une ville donnée.
    Utilisez cet outil dès que l'utilisateur vous demande la météo ou le temps qu'il fait dans un lieu."""
    city_lower = city.lower()
    if "kinshasa" in city_lower:
        return json.dumps(
            {"temp": "31°C", "condition": "Orageux", "title": "Météo Kinshasa"}
        )
    elif "paris" in city_lower:
        return json.dumps(
            {"temp": "14°C", "condition": "Pluvieux", "title": "Météo Paris"}
        )
    return json.dumps(
        {"temp": "22°C", "condition": "Clément", "title": f"Météo {city}"}
    )


@tool
def generate_sales_metrics(period: str) -> str:
    """Génère des mesures de ventes et des données chiffrées pour un graphique.
    L'argument 'period' doit être 'semaine', 'mois' ou 'année'. Use activement cet outil si on demande des stats."""
    period_lower = period.lower()
    if "semaine" in period_lower:
        return json.dumps(
            {
                "title": "Ventes Hebdomadaires",
                "labels": ["Lun", "Mar", "Mer", "Jeu", "Ven"],
                "values": [120.0, 240.5, 180.0, 310.2, 450.0],
            }
        )
    elif "mois" in period_lower:
        return json.dumps(
            {
                "title": "Rapport Mensuel",
                "labels": ["Janv", "Févr", "Mars"],
                "values": [1200.0, 1850.0, 1400.0],
            }
        )
    return json.dumps(
        {
            "title": "Évolution Annuelle",
            "labels": ["2024", "2025", "2026"],
            "values": [5800.0, 6200.0, 7100.0],
        }
    )


# Liste et nœud officiels LangGraph
tools = [fetch_live_weather, generate_sales_metrics]
tool_node = ToolNode(tools)

# --- SCHÉMAS DE RENDU FLET ---


class UIButtonSchema(BaseModel):
    text: str = Field(default="")
    action_key: str = Field(default="")


class UIComponentSchema(BaseModel):
    component_type: Literal["none", "weather_card", "bar_chart"] = Field("none")
    title: Optional[str] = Field(default=None)
    weather_city: Optional[str] = Field(default=None)
    weather_temp: Optional[str] = Field(default=None)
    chart_labels: Optional[List[str]] = Field(default_factory=list)
    chart_values: Optional[List[float]] = Field(default_factory=list)
    action_button: Optional[UIButtonSchema] = Field(default=None)


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    last_ui: Optional[UIComponentSchema] = None


# Prompt purement orienté sur le rôle de l'assistant
SYSTEM_PROMPT = SystemMessage(
    content="Tu es un assistant virtuel conversationnel doté d'outils de pointe. "
    "Réponds de manière chaleureuse en français. Si l'action requiert des données "
    "externes (météo, graphiques), appelle l'outil adéquat mis à ta disposition."
)


# NŒUD 1 : L'assistant délègue à 100% le function calling à LangChain
def assistant_node(state: AgentState):
    global llm
    if llm is None:
        setup_llm_model("http://127.0.0", "lm-studio", "qwen/qwen3-1.7b@q8_0")

    # 1. On lie proprement les outils au LLM
    llm_with_tools = llm.bind_tools(tools)

    # 2. On invoque LangChain de manière standard
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state.messages)

    # 3. Retour direct du message de l'IA (LangGraph gère les tool_calls natifs de la réponse)
    return {"messages": [response], "last_ui": UIComponentSchema(component_type="none")}


# NŒUD 3 : Construit l'interface à partir des messages d'outils présents dans l'état
def render_ui_node(state: AgentState):
    """Génère l'interface visuelle Flet UNIQUEMENT si un outil vient d'être exécuté au cours de ce tour."""
    if not state.messages:
        return {"last_ui": UIComponentSchema(component_type="none")}

    # On récupère le TOUT DERNIER message de la conversation
    last_message = state.messages[-1]

    # Si le tout dernier message est un ToolMessage, cela signifie qu'un outil
    # vient de tourner à l'instant. On génère le widget adéquat.
    if isinstance(last_message, ToolMessage):
        try:
            tool_output = json.loads(f"{last_message.content}")

            # Cas A : Outil Graphique
            if "values" in tool_output:
                ui_comp = UIComponentSchema(
                    component_type="bar_chart",
                    title=tool_output["title"],
                    chart_labels=tool_output["labels"],
                    chart_values=tool_output["values"],
                    action_button=UIButtonSchema(text="Exporter", action_key="export"),
                )
                return {"last_ui": ui_comp}

            # Cas B : Outil Météo
            elif "temp" in tool_output:
                ui_comp = UIComponentSchema(
                    component_type="weather_card",
                    title=tool_output["title"],
                    weather_city=tool_output["title"].split()[-1],
                    weather_temp=tool_output["temp"],
                    action_button=UIButtonSchema(
                        text="Actualiser", action_key="refresh"
                    ),
                )
                return {"last_ui": ui_comp}
        except Exception as e:
            logging.error(f"Error parsing tool message: {e}")

    # SÉCURITÉ CRITIQUE : Si le dernier message n'est pas un outil (ex: discussion simple),
    # on écrase explicitement l'état précédent pour ne pas ré-afficher l'ancien widget.
    return {"last_ui": UIComponentSchema(component_type="none")}


def should_continue(state: AgentState):
    """Routeur conditionnel utilisant l'API native de LangGraph."""
    last_message: AnyMessage | ToolMessage = state.messages[-1]
    # LangChain remplit cet attribut si le modèle a choisi d'exécuter une fonction
    # if isinstance(last_message, ToolMessage):
    if hasattr(last_message, "tool_calls"):
        return "tools"
    return "end"


# --- ASSEMBLAGE DU GRAPH ---
builder = StateGraph(AgentState)
builder.add_node("assistant", assistant_node)
builder.add_node("tools", tool_node)
builder.add_node("render_ui", render_ui_node)

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant", should_continue, {"tools": "tools", "end": "render_ui"}
)
builder.add_edge("tools", "render_ui")
builder.add_edge("render_ui", END)

agent_app = builder.compile()
