from google.adk.agents import Agent
from tools.search_products import search_products
from constants import (
    OP_AND, OP_OR, OP_NOT,
    OP_EQ, OP_NE, OP_LT, OP_LTE, OP_GT, OP_GTE, OP_CONTAINS,
)

_LOGICAL_OPS_STR = "|".join(f'"{op.upper()}"' for op in (OP_AND, OP_OR))
_COMPARISON_OPS_STR = "|".join(
    f'"{op.upper()}"' for op in (OP_EQ, OP_NE, OP_LT, OP_LTE, OP_GT, OP_GTE, OP_CONTAINS)
)

root_agent = Agent(
    name="product_finder",
    model="gemini-2.5-flash",
    description="Helps users find products using natural language queries.",
    instruction=f"""You are a helpful product finder assistant.

When a user asks about products, call search_products with a JSON filter tree.

Filter tree rules:
- AND/OR node:   {{"op": {_LOGICAL_OPS_STR}, "conditions": [...]}}
- NOT node:     {{"op": "{OP_NOT.upper()}", "conditions": [<exactly one node>]}}
- Leaf node: {{"field": "category"|"price"|"name", "op": {_COMPARISON_OPS_STR}, "value": <string or number>}}
- category values must be one of: clothing, electronics, accessories, groceries
- Omit filters (pass empty string) to return all products.

After retrieving results, reply naturally and append:
<PRODUCTS_JSON>[the products array from the tool result]</PRODUCTS_JSON>

If no products match, tell the user politely and do not append the block.""",
    tools=[search_products],
)
