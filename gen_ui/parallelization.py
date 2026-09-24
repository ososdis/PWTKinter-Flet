# With parallelization, LLMs work simultaneously on a task.
# This is either done by running multiple independent subtasks at the same time, or running the same task multiple times to check for different outputs.
# Parallelization is commonly used to:
# - Split up subtasks and run them in parallel, which increases speed
# - Run tasks multiple times to check for different outputs, which increases confidence
# Some examples include:
# - Running one subtask that processes a document for keywords, and a second subtask to check for formatting errors
# - Running a task multiple times that scores a document for accuracy based on different criteria, like the number of citations, the number of sources used, and the quality of the sources

# - Sub-tasks can be parallelized.
#     - E.g., when you want multi-perspectives for one task  multi-query for RAG).
#     - E.g., when independent tasks can be performed w/ different prompts.

# Example:

# - Take a topic, create a joke, story, and poem
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
    story: str
    poem: str
    combined_output: str


# Nodes
def call_llm_1(state: State):
    """First LLM call to generate initial joke"""

    msg = llm.invoke(f"Write a joke about {state['topic']}")
    return {"joke": msg.content}


def call_llm_2(state: State):
    """Second LLM call to generate story"""

    msg = llm.invoke(f"Write a story about {state['topic']}")
    return {"story": msg.content}


def call_llm_3(state: State):
    """Third LLM call to generate poem"""

    msg = llm.invoke(f"Write a poem about {state['topic']}")
    return {"poem": msg.content}


def aggregator(state: State):
    """Combine the joke, story and poem into a single output"""

    combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
    combined += f"STORY:\n{state['story']}\n\n"
    combined += f"JOKE:\n{state['joke']}\n\n"
    combined += f"POEM:\n{state['poem']}"
    return {"combined_output": combined}


# Build workflow
parallel_builder = StateGraph(State)

# Add nodes
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")
parallel_builder.add_edge("aggregator", END)
parallel_workflow = parallel_builder.compile()

# Show workflow
# display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

# Invoke
state = cast(
    State,
    parallel_workflow.invoke(
        State(
            {
                "topic": "cats",
                "combined_output": "",
                "joke": "",
                "story": "",
                "poem": "",
            }
        )
    ),
)
print(state["combined_output"])
