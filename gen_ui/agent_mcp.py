import asyncio
import os

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

# from pydantic import BaseModel, Field
from typing_extensions import cast

# from IPython.display import Image, display

os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:1234/v1"
os.environ["OPENAI_API_KEY"] = "lm_studio"

llm = ChatOpenAI(model="qwen3-1.7b@q8_0")


async def main():
    client = MultiServerMCPClient(
        {
            "test_mcp": {
                "transport": "stdio",
                "command": "uv",
                # chemin complet du script à exécuter
                "args": [
                    "run",
                    "--with",
                    "fastmcp",
                    "fastmcp",
                    "run",
                    "/home/oscardisu/Downloads/gameTeachers (1)/gen_ui/mcp_test.py",
                ],
            },
            "domotique": {
                "transport": "stdio",
                "command": "uv",
                # chemin complet du script à exécuter
                "args": [
                    "run",
                    "--with",
                    "fastmcp",
                    "fastmcp",
                    "run",
                    "/home/oscardisu/Downloads/gameTeachers (1)/gen_ui/serveur_mqtt_mcp.py",
                ],
            },
        }
    )
    tools = await client.get_tools()
    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)

    print(f"Outils charges: {[tool.name for tool in tools]}")

    async def llm_call(state: MessagesState):
        """LLM decide si un outil doit être appelé"""
        response = await llm_with_tools.ainvoke(
            [
                SystemMessage(
                    content="Tu es un agent qui peut appeler des outils pour résoudre des problèmes"
                )
            ]
            + state["messages"]
        )
        return {"messages": [response]}

    async def tool_node(state: MessagesState):
        """Realise l'appel des outils"""
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for tool_call in tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(tool_call["args"])
            results.append(
                ToolMessage(content=observation, tool_call_id=tool_call["id"])
            )
        return {"messages": results}

    async def should_continue(state: MessagesState):
        """Détermine si l'agent doit continuer à appeler des outils ou terminer"""
        messages = state["messages"]
        last_message = messages[-1]
        # Si le dernier message est un appel d'outil, continuer à appeler des outils
        if last_message.tool_calls:
            return "tool_node"
        # Sinon, terminer
        return END

    # Créer le graphe
    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    # Connecter les nodes
    agent_builder.add_edge(START, "llm")
    agent_builder.add_conditional_edges("llm", should_continue, ["tool_node", END])
    agent_builder.add_edge("tool_node", "llm")
    # Compiler
    agent = agent_builder.compile()

    # Invoke
    # L'utilisateur saisi des requetes sur input dans une boucle, la boucle continue jusqu'à ce que l'utilisateur saisisse "exit"
    while True:
        user_input = input("Enter a request (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        messages = [HumanMessage(content=user_input)]
        messages = await agent.ainvoke(cast(MessagesState, {"messages": messages}))

        for m in messages["messages"]:
            m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
