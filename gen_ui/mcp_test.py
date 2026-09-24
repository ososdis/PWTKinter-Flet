from fastmcp import FastMCP

mcp = FastMCP("Simple MCP Server")


@mcp.tool(name="addition", description="Fais la somme de deux nombres")
async def add(a: int, b: int) -> int:
    return a + b


@mcp.tool(name="subtraction", description="Fais la différence de deux nombres")
async def subtract(a: int, b: int) -> int:
    return a - b


@mcp.tool(name="multiplication", description="Fais le produit de deux nombres")
async def multiply(a: int, b: int) -> int:
    return a * b


@mcp.tool(name="division", description="Fais le quotient de deux nombres")
async def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


if __name__ == "__main__":
    mcp.run()
