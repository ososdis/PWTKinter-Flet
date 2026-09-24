import os

from langchain_openai import ChatOpenAI
from langgraph.pregel.main import cast
from pydantic import BaseModel, Field

os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"
os.environ["OPENAI_API_KEY"] = "lm_studio"

llm = ChatOpenAI(model="qwen3-1.7b@q8_0")


class SearchQuery(BaseModel):
    search_query: str = Field(
        description="Requête optimisée pour une recherche sur le web."
    )
    justification: str = Field(
        description="Explication de la pertinence de cette requête par rapport à la demande de l'utilisateur."
    )


# Augment the LLM with schema for structured output
structured_llm = llm.with_structured_output(SearchQuery)

# Invoke the augmented LLM
output = cast(
    SearchQuery,
    structured_llm.invoke(
        "Quel est le lien entre le score de calcium coronaire (CT score) et un taux de cholestérol élevé ?"
    ),
)
print(output.search_query)
print(output.justification)


# Define a tool
def multiply(a: int, b: int) -> int:
    return a * b


# Augment the LLM with tools
llm_with_tools = llm.bind_tools([multiply])

# Invoke the LLM with input that triggers the tool call
msg = llm_with_tools.invoke("What is 5 times 5? and then times 10 ?")

# Get the tool call
print(msg.tool_calls)
print(msg.additional_kwargs.get("content"))
