# Prompt chaining
# Prompt chaining is when each LLM call processes the output of the previous call.
# It’s often used for performing well-defined tasks that can be broken down into smaller, verifiable steps. Some examples include:
# - Translating documents into different languages
# - Verifying generated content for consistency
#
# Example:
#
# - Take a topic, LLM makes a joke, check the joke, improve it twice
#

import os

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

# from pydantic import BaseModel, Field
from typing_extensions import TypedDict, cast

# from IPython.display import Image, display

os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"
os.environ["OPENAI_API_KEY"] = "lm_studio"

llm = ChatOpenAI(model="qwen3-1.7b@q8_0")


# Graph state
class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str


# Nodes
def generate_joke(state: State):
    """First LLM call to generate initial joke"""

    msg = llm.invoke(f"Ecris une blague courte sur {state['topic']}")
    state["joke"] = f"{msg.content}"
    return state


def check_punchline(state: State):
    """Gate function to check if the joke has a punchline"""

    # Simple check - does the joke contain "?" or "!"
    if "?" in state["joke"] or "!" in state["joke"]:
        return "Pass"
    return "Fail"


def improve_joke(state: State):
    """Second LLM call to improve the joke"""

    msg = llm.invoke(
        f"Rend la blague plus amusante en ajoutant des mots de jeu: {state['joke']}"
    )
    state["improved_joke"] = f"{msg.content}"
    return state


def polish_joke(state: State):
    """Third LLM call for final polish"""
    msg = llm.invoke(f"Ajoute une surprise à cette blague: {state['improved_joke']}")
    state["final_joke"] = f"{msg.content}"
    return state


# Build workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("generate_joke", generate_joke)
workflow.add_node("improve_joke", improve_joke)
workflow.add_node("polish_joke", polish_joke)

# Add edges to connect nodes
workflow.add_edge(START, "generate_joke")
workflow.add_conditional_edges(
    "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
)
workflow.add_edge("improve_joke", "polish_joke")
workflow.add_edge("polish_joke", END)

# Compile
chain = workflow.compile()

# Show workflow
# display(Image(chain.get_graph().draw_mermaid_png()))

# Invoke
state = cast(
    State,
    chain.invoke(
        State(
            {"topic": "les chiens", "joke": "", "improved_joke": "", "final_joke": ""}
        )
    ),
)
print("Initial joke:")
print(state["joke"])
print("\n--- ----- ---\n")
if "improved_joke" in state:
    print("Improved joke:")
    print(state["improved_joke"])
    print("\n--- ----- ---\n")

    print("Final joke:")
    print(state["final_joke"])
else:
    print("Final joke:")
    print(state["joke"])
