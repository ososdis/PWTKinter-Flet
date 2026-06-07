import json
import logging
from typing import Annotated, List, Literal, Optional

from flet_web.fastapi.flet_app import os
from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
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
    Utilisez cet outil dès que l'utilisateur demande le temps qu'il fait."""
    city_lower = city.lower()
    if "kinshasa" in city_lower:
        return json.dumps(
            {"temp": "31°C", "condition": "Orageux", "title": "Météo Kinshasa (Live)"}
        )
    elif "paris" in city_lower:
        return json.dumps(
            {"temp": "14°C", "condition": "Pluvieux", "title": "Météo Paris (Live)"}
        )
    return json.dumps(
        {"temp": "22°C", "condition": "Clément", "title": f"Météo {city}"}
    )


# --- AJOUT DU DEUXIÈME TOOL DANS AGENT.PY ---


@tool
def generate_sales_metrics(period: str) -> str:
    """Génère des mesures de ventes et des statistiques financières pour une période donnée ('semaine', 'mois', 'année').
    Utilisez cet outil dès que l'utilisateur demande un graphique, des ventes ou des statistiques."""
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
                "title": "Rapport Mensuel (Trimestre)",
                "labels": ["Janv", "Févr", "Mars"],
                "values": [1200.0, 1850.0, 1400.0],
            }
        )
    # Valeur par défaut : Année
    return json.dumps(
        {
            "title": "Évolution Annuelle",
            "labels": ["2023", "2024", "2025", "2026"],
            "values": [4500.0, 5800.0, 6200.0, 7100.0],
        }
    )


# Enregistrement de la liste officielle des outils LangGraph
tools = [fetch_live_weather, generate_sales_metrics]
tool_node = ToolNode(tools)

# --- SCHÉMAS DE DONNÉES RENDU GENUI ---


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


SYSTEM_PROMPT = SystemMessage(
    content=(
        "Tu es un assistant virtuel GenUI. Tu dois TOUJOURS répondre exclusivement au format JSON strict, sans texte explicatif en dehors.\n\n"
        "Exemple de réponse si l'utilisateur demande la météo :\n"
        "{\n"
        '  "chat_response": "Voici la météo actuelle pour Kinshasa.",\n'
        '  "ui_component": {\n'
        '    "component_type": "weather_card",\n'
        '    "title": "Météo Kinshasa",\n'
        '    "weather_city": "Kinshasa",\n'
        '    "weather_temp": "28°C",\n'
        '    "chart_labels": [],\n'
        '    "chart_values": [],\n'
        '    "action_button": {\n'
        '      "text": "Rafraîchir",\n'
        '      "action_key": "refresh_weather"\n'
        "    }\n"
        "  }\n"
        "}\n\n"
        "Exemple de réponse pour une discussion normale (sans composant) :\n"
        "{\n"
        '  "chat_response": "Bonjour ! Comment puis-je t\'aider aujourd\'hui ?",\n'
        '  "ui_component": {\n'
        '    "component_type": "none",\n'
        '    "title": null,\n'
        '    "weather_city": null,\n'
        '    "weather_temp": null,\n'
        '    "chart_labels": [],\n'
        '    "chart_values": [],\n'
        '    "action_button": null\n'
        "  }\n"
        "}\n\n"
        "Respecte scrupuleusement ces structures JSON sans ajouter de fioritures ni de blocs de code markdown."
    )
)


# --- MISE À JOUR DES NŒUDS DE ROUTAGE ET RENDU ---


def assistant_node(state: AgentState):
    global llm
    if llm is None:
        setup_llm_model("http://192.168.170", "lm-studio", "qwen/qwen3-1.7b@q6_k")

    response = llm.invoke([SYSTEM_PROMPT] + state.messages)

    raw_text = response.content if response.content else ""
    if not raw_text and hasattr(response, "additional_kwargs"):
        raw_text = response.additional_kwargs.get("reasoning_content", "")

    raw_text = str(raw_text).strip().lower()

    # Détection Tool 1 : Météo
    if "météo" in raw_text or "weather" in raw_text or "fetch_live_weather" in raw_text:
        city = "Kinshasa" if "kinshasa" in raw_text else "Paris"
        return {
            "messages": [
                AIMessage(
                    content="Appel de l'outil météo...",
                    tool_calls=[
                        {
                            "name": "fetch_live_weather",
                            "args": {"city": city},
                            "id": "call_weather",
                        }
                    ],
                )
            ]
        }

    # Détection Tool 2 : Graphique / Ventes
    elif (
        "graphique" in raw_text
        or "ventes" in raw_text
        or "statistiques" in raw_text
        or "metrics" in raw_text
    ):
        period = "semaine"
        if "mois" in raw_text:
            period = "mois"
        elif "année" in raw_text or "an" in raw_text:
            period = "année"

        return {
            "messages": [
                AIMessage(
                    content="Génération du graphique demandé...",
                    tool_calls=[
                        {
                            "name": "generate_sales_metrics",
                            "args": {"period": period},
                            "id": "call_metrics",
                        }
                    ],
                )
            ]
        }

    return {
        "messages": [AIMessage(content=raw_text)],
        "last_ui": UIComponentSchema(component_type="none"),
    }


def render_ui_node(state: AgentState):
    last_message = state.messages[-1]

    if isinstance(last_message, ToolMessage):
        tool_output = json.loads(f"{last_message.content}")

        # Rend la structure adaptée si l'outil exécuté est l'outil graphique
        if "labels" in tool_output and "values" in tool_output:
            ui_comp = UIComponentSchema(
                component_type="bar_chart",
                title=tool_output["title"],
                chart_labels=tool_output["labels"],
                chart_values=tool_output["values"],
                action_button=UIButtonSchema(
                    text="Exporter PDF", action_key="export_pdf"
                ),
            )
            return {
                "messages": [
                    AIMessage(content="Voici vos statistiques consolidées en direct.")
                ],
                "last_ui": ui_comp,
            }

        # Rend la structure adaptée si l'outil exécuté est l'outil météo
        else:
            ui_comp = UIComponentSchema(
                component_type="weather_card",
                title=tool_output["title"],
                weather_city=tool_output["title"].split()[-1],
                weather_temp=tool_output["temp"],
                action_button=UIButtonSchema(text="Actualiser", action_key="refresh"),
            )
            return {
                "messages": [AIMessage(content="Météo récupérée via l'API locale.")],
                "last_ui": ui_comp,
            }

    return {"last_ui": UIComponentSchema(component_type="none")}


# Routeur conditionnel pour aiguiller le graphe
def should_continue(state: AgentState):
    last_message = state.messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"


# Assemblage du Graphe
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
