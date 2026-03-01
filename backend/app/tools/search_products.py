import json
from pathlib import Path
from constants import *

PRODUCTS_PATH = Path(__file__).resolve().parent.parent / "data/products.json"

def _eval_node(product: dict, node: dict) -> bool:
    """Recursively evaluate a filter tree node against a product."""
    op = node["op"].lower()

    if op in LOGICAL_OPS:
        conditions = node.get("conditions", [])
        if op == OP_NOT:
            if len(conditions) != 1:
                raise ValueError(f"NOT node must have exactly 1 condition, got {len(conditions)}")
            return not _eval_node(product, conditions[0])
        if op == OP_AND:
            return all(_eval_node(product, child) for child in conditions)
        return any(_eval_node(product, child) for child in conditions)

    # Leaf node
    field = node["field"].lower()
    cmp_op = op
    value = node["value"]
    product_value = product.get(field)

    if field == "category":
        product_value = (product_value or "").lower()
        value = value.lower() if isinstance(value, str) else value

    if cmp_op == OP_EQ:
        return product_value == value
    elif cmp_op == OP_NE:
        return product_value != value
    elif cmp_op == OP_LT:
        return product_value < value
    elif cmp_op == OP_LTE:
        return product_value <= value
    elif cmp_op == OP_GT:
        return product_value > value
    elif cmp_op == OP_GTE:
        return product_value >= value
    elif cmp_op == OP_CONTAINS:
        return value.lower() in str(product_value).lower()

    return True


def search_products(filters: str = "") -> dict:
    """Search and filter products using a nested boolean filter expression.

    Args:
        filters: A JSON string encoding a filter expression tree.
                 Leave empty or omit to return all products.

                 Two node types:

                 1. Logical node:
                    {"op": "AND" | "OR", "conditions": [<node>, ...]}
                    {"op": "NOT", "conditions": [<exactly one node>]}

                 2. Leaf node:
                    {"field": "category" | "price" | "name",
                     "op": "eq" | "ne" | "lt" | "lte" | "gt" | "gte" | "contains",
                     "value": <string or number>}

                 Example — (category is "clothing" OR "accessories") AND (price < 10 OR price > 40) AND NOT (name contains "sale"):
                 {
                   "op": "AND",
                   "conditions": [
                     {"op": "OR", "conditions": [
                       {"field": "category", "op": "eq", "value": "clothing"},
                       {"field": "category", "op": "eq", "value": "accessories"}
                     ]},
                     {"op": "OR", "conditions": [
                       {"field": "price", "op": "lt", "value": 10},
                       {"field": "price", "op": "gt", "value": 40}
                     ]},
                     {"op": "NOT", "conditions": [
                       {"field": "name", "op": "contains", "value": "jacket"}
                     ]}
                   ]
                 }

    Returns:
        A dict with 'status' and either 'products' list or 'message' string.
    """
    with open(PRODUCTS_PATH, "r") as f:
        products = json.load(f)

    if not filters:
        results = products
    else:
        try:
            filter_tree = json.loads(filters)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid filter JSON: {e}"}

        try:
            results = [p for p in products if _eval_node(p, filter_tree)]
        except (KeyError, TypeError, ValueError) as e:
            return {"status": "error", "message": f"Invalid filter structure: {e}"}

    if not results:
        return {
            "status": "no_results",
            "message": "No products found matching your criteria.",
        }

    return {"status": "success", "products": results}
