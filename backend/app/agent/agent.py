from google.adk.agents import Agent
from tools.search_products import search_products

root_agent = Agent(
    name="product_finder",
    model="gemini-2.5-flash",
    description="Helps users find products using natural language queries.",
    instruction="""You are a helpful product finder assistant.

When a user asks about products, call search_products with a JSON filter tree.

Filter tree rules:
- AND/OR node:   {"op": "AND"|"OR", "conditions": [...]}
- NOT node:     {"op": "NOT", "conditions": [<exactly one node>]}
- Leaf node: {"field": "category"|"price"|"name", "op": "eq"|"ne"|"lt"|"lte"|"gt"|"gte"|"contains", "value": <string or number>}
- category values must be one of: clothing, electronics, accessories, groceries
- Omit filters (pass empty string) to return all products.

After retrieving results, reply naturally and append:
<PRODUCTS_JSON>[the products array from the tool result]</PRODUCTS_JSON>

If no products match, tell the user politely and do not append the block.""",
    tools=[search_products],
)
