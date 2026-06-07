# import getpass
#
import json
import logging
import os
from typing import Annotated, List, Literal, Optional  # , TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.tools import tool

# from langchain_core.messages.chat import ChatMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"

# Variable globale pour l'instance LLM modifiable dynamiquement


def setup_llm_model(base_url: str, api_key: str, model_name: str | None):
    """Fonction appelée par Flet pour initialiser l'IA avec vos choix d'écran."""
    global llm
    os.environ["OPENAI_API_KEY"] = api_key
    if model_name:
        llm = ChatOpenAI(base_url=base_url, model=model_name, temperature=0.3)
    os.environ["OPENAI_BASE_URL"] = base_url


@tool
def fetch_live_weather(city: str) -> str:
    """Consulte les conditions météorologiques actuelles pour une ville donnée.
    Utilise cet outil dès que l'utilisateur demande le temps qu'il fait."""
    city_lower = city.lower()
    if "kinshasa" in city_lower:
        return json.dumps({"temp": "31°C", "condition": "Orageux", "humidity": "85%"})
    elif "paris" in city_lower:
        return json.dumps({"temp": "14°C", "condition": "Pluvieux", "humidity": "60%"})
    return json.dumps({"temp": "22°C", "condition": "Clément", "humidity": "50%"})


# Regroupement des outils dans la liste de référence LangChain
tools_list = [fetch_live_weather]


# Schéma pour un bouton généré dynamiquement
class UIButtonSchema(BaseModel):
    text: str = Field(
        default="",
        description="Le texte à afficher sur le bouton (ex: 'Valider', 'Rafraîchir')",
    )
    action_key: str = Field(
        default="",
        description="Un identifiant unique pour l'action (ex: 'validate_payment', 'retry_weather')",
    )


class UIComponentSchema(BaseModel):
    component_type: Literal["none", "weather_card", "bar_chart"] = Field("none")
    title: Optional[str] = Field(default=None)
    weather_city: Optional[str] = Field(default=None)
    weather_temp: Optional[str] = Field(default=None)
    chart_labels: Optional[List[str]] = Field(
        default_factory=list
    )  # Évite les conflits de listes mutables
    chart_values: Optional[List[float]] = Field(default_factory=list)
    action_button: Optional[UIButtonSchema] = Field(default=None)


class LLMResponseSchema(BaseModel):
    chat_response: str = Field(description="Votre réponse textuelle.")
    ui_component: Optional[UIComponentSchema] = Field(None)


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    last_ui: Optional[UIComponentSchema]


# structured_llm = llm.with_structured_output(schema=LLMResponseSchema)

# SYSTEM_PROMPT = SystemMessage(
#     content="Tu es un assistant conversationnel GenUI. Si l'utilisateur demande une action critique "
#     "(comme valider, confirmer, ou actualiser), génère le composant avec un 'action_button' approprié."
# )

# TODO: Regler le Problem des tools calling

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


# SYSTEM_PROMPT = SystemMessage(
#    content=(
#        "Tu es un assistant virtuel GenUI doté d'outils. Tu dois impérativement répondre sous forme d'un objet JSON strict.\n"
#        "Si l'utilisateur demande la météo, tu dois formuler ta réponse en deux volets :\n"
#        "1. Choisir d'exécuter l'outil approprié en interne.\n"
#        "2. Structurer ton JSON final selon le schéma ci-dessous, en te basant sur les données récoltées :\n\n"
#        "{\n"
#        '  "chat_response": "Explication textuelle de la météo pour l\'utilisateur.",\n'
#        '  "ui_component": {\n'
#        '    "component_type": "weather_card",\n'
#        '    "title": "Météo en direct",\n'
#        '    "weather_city": "Nom de la ville",\n'
#        '    "weather_temp": "La température récupérée via l\'outil",\n'
#       '    "action_button": {"text": "Actualiser", "action_key": "refresh"}\n'
#        "  }\n"
#        "}"
#    )
# )


# def assistant_node(state: AgentState) -> AgentState:
#    response = structured_llm.invoke(input=[SYSTEM_PROMPT] + state.messages)
#    aimessage = AIMessage(content=response["chat_response"])
#    chatmessage: list[AnyMessage] = [aimessage]
#    return AgentState(messages=chatmessage, last_ui=response["ui_component"])
def assistant_node(state: AgentState):
    global llm
    if llm is None:
        # Fallback de sécurité si Flet n'a pas encore appelé setup_llm_model
        llm = ChatOpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL"),
            temperature=0.3,
            model="qwen3-1.7b@q6_k",  # "nvidia/nemotron-3-nano-4b",
        )
    # response = llm.invoke([SYSTEM_PROMPT] + state.messages)
    llm_with_tools = llm.bind_tools(tools_list)  # insert langchain tool calling
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state.messages)
    logging.info(f"assistant_node: response={response}")
    raw_text = ""

    # 1. Extraction sécurisée selon le type de response.content
    if response.content:
        if isinstance(response.content, str):
            raw_text = response.content
        elif isinstance(response.content, list):
            parts = []
            for part in response.content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict) and part.get("type") == "text":
                    parts.append(part.get("text", ""))
            raw_text = "".join(parts)

    # 2. Extraction pour les modèles "Thinking" de LM Studio
    if not raw_text:
        if hasattr(response, "additional_kwargs") and response.additional_kwargs:
            raw_text = response.additional_kwargs.get("reasoning_content", "")
        elif hasattr(response, "response_metadata") and response.response_metadata:
            message_dict = response.response_metadata.get("message", {})
            raw_text = message_dict.get("reasoning_content", "")

        if not raw_text and hasattr(response, "reasoning_content"):
            raw_text = getattr(response, "reasoning_content", "")

    raw_text = str(raw_text)
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw_text)
        parsed_response = LLMResponseSchema(**data)
        chat_msg = parsed_response.chat_response
        ui_comp = parsed_response.ui_component
    except Exception as e:
        logging.error(f"Failed to parse response: {e}")
        chat_msg = (
            raw_text if raw_text else "Désolé, impossible de formater l'interface."
        )
        # Évite le crash si state.last_ui est absent à l'initialisation
        ui_comp = (
            state.last_ui if state.last_ui else UIComponentSchema(component_type="none")
        )

    # CORRECTION : On construit un objet AIMessage propre pour le réducteur add_messages
    new_message = AIMessage(content=chat_msg)

    # CORRECTION : Retourner un dictionnaire compatible avec les propriétés de mise à jour du BaseModel
    return AgentState(
        messages=[new_message],  # Le réducteur va l'ajouter à l'historique existant
        last_ui=ui_comp,
    )


builder = StateGraph(AgentState)
builder.add_node("assistant", assistant_node)
builder.add_edge(START, "assistant")
builder.add_edge("assistant", END)
agent_app = builder.compile()
