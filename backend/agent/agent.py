import json
from pathlib import Path
from google.adk.agents import Agent

PRODUCTS_PATH = Path(__file__).resolve().parent.parent.parent / "products.json"

def search_products(
    category: str = "",
    min_price: float = 0,
    max_price: float = 0,
) -> dict:
    """Search and filter products by category and/or price range.

    Args:
        category: Product category to filter by (e.g. "electronics", "clothing",
                  "groceries", "accessories"). Case-insensitive. Empty string means
                  no category filter.
        min_price: Minimum price filter (inclusive). 0 means no minimum.
        max_price: Maximum price filter (inclusive). 0 means no maximum.

    Returns:
        A dict with 'status' and either 'products' list or 'message' string.
    """
    with open(PRODUCTS_PATH, "r") as f:
        products = json.load(f)

    results = products

    if category:
        results = [
            p for p in results if p["category"].lower() == category.lower()
        ]

    if min_price > 0:
        results = [p for p in results if p["price"] >= min_price]

    if max_price > 0:
        results = [p for p in results if p["price"] <= max_price]

    if not results:
        return {
            "status": "no_results",
            "message": "No products found matching your criteria.",
        }

    return {"status": "success", "products": results}

import json
import os
from google.adk.agents import Agent

# Load products.json once at import time (two levels up from this file)
_PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "products.json")
with open(os.path.abspath(_PRODUCTS_PATH), "r", encoding="utf-8") as _f:
    _PRODUCTS: list[dict] = json.load(_f)

_VALID_CATEGORIES = {"clothing", "electronics", "accessories", "groceries"}
_VALID_OPERATORS = {">", "<", "=", ">=", "<="}


def _apply_price_filter(products: list[dict], operator: str, price: float) -> list[dict]:
    ops = {
        ">": lambda p: p > price,
        "<": lambda p: p < price,
        "=": lambda p: p == price,
        ">=": lambda p: p >= price,
        "<=": lambda p: p <= price,
    }
    fn = ops.get(operator)
    if fn is None:
        return []
    return [p for p in products if fn(p["price"])]


def get_products_by_category(category: str) -> dict:
    """Filter products by category.

    Args:
        category: One of 'clothing', 'electronics', 'accessories', 'groceries'.

    Returns:
        A dict with status, products list, and count.
    """
    cat = category.strip().lower()
    if cat not in _VALID_CATEGORIES:
        return {
            "status": "error",
            "message": f"Invalid category '{category}'. Valid: {sorted(_VALID_CATEGORIES)}",
            "products": [],
            "count": 0,
        }
    results = [p for p in _PRODUCTS if p["category"].lower() == cat]
    return {"status": "success", "products": results, "count": len(results)}


def get_products_by_price(operator: str, price: float) -> dict:
    """Filter products by price using a comparison operator.

    Args:
        operator: One of '>', '<', '=', '>=', '<='.
        price: The price threshold to compare against.

    Returns:
        A dict with status, products list, and count.
    """
    op = operator.strip()
    if op not in _VALID_OPERATORS:
        return {
            "status": "error",
            "message": f"Invalid operator '{operator}'. Valid: {sorted(_VALID_OPERATORS)}",
            "products": [],
            "count": 0,
        }
    results = _apply_price_filter(_PRODUCTS, op, float(price))
    return {"status": "success", "products": results, "count": len(results)}


def get_products_by_category_and_price(category: str, operator: str, price: float) -> dict:
    """Filter products by both category and price.

    Args:
        category: One of 'clothing', 'electronics', 'accessories', 'groceries'.
        operator: One of '>', '<', '=', '>=', '<='.
        price: The price threshold to compare against.

    Returns:
        A dict with status, products list, and count.
    """
    cat = category.strip().lower()
    if cat not in _VALID_CATEGORIES:
        return {
            "status": "error",
            "message": f"Invalid category '{category}'. Valid: {sorted(_VALID_CATEGORIES)}",
            "products": [],
            "count": 0,
        }
    op = operator.strip()
    if op not in _VALID_OPERATORS:
        return {
            "status": "error",
            "message": f"Invalid operator '{operator}'. Valid: {sorted(_VALID_OPERATORS)}",
            "products": [],
            "count": 0,
        }
    by_cat = [p for p in _PRODUCTS if p["category"].lower() == cat]
    results = _apply_price_filter(by_cat, op, float(price))
    return {"status": "success", "products": results, "count": len(results)}


root_agent = Agent(
    name="product_finder_agent",
    model="gemini-2.5-flash",
    description="Product finder that filters by category and price.",
    instruction="""
You are a helpful product finder assistant.
Categories available: clothing, electronics, accessories, groceries.

Map natural language to operators:
- "under/less than/cheaper than $X" → operator="<"
- "over/more than/above $X" → operator=">"
- "exactly/costs $X" → operator="="
- "$X or less/up to $X" → operator="<="
- "$X or more/at least $X" → operator=">="

Always call the appropriate tool. After your friendly response, if products
were found, append exactly:

<PRODUCTS_JSON>
[...raw products array from tool result as valid JSON...]
</PRODUCTS_JSON>
""",
    tools=[get_products_by_category, get_products_by_price, get_products_by_category_and_price],
)
