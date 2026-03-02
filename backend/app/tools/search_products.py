import json
import operator
from pathlib import Path
from constants import (
    OP_AND, OP_OR, OP_NOT, LOGICAL_OPS,
    OP_EQ, OP_NE, OP_LT, OP_LTE, OP_GT, OP_GTE, OP_CONTAINS, COMPARISON_OPS,
)
from schemas.product import Product
from pydantic import TypeAdapter

PRODUCTS_PATH = Path(__file__).resolve().parent.parent / "data/products.json"

with open(PRODUCTS_PATH, "r") as _f:
    _PRODUCTS: list[Product] = TypeAdapter(list[Product]).validate_json(_f.read())

_ALLOWED_FIELDS = {"category", "price", "name"}

_COMPARISON_FUNCS = {
    OP_EQ: operator.eq,
    OP_NE: operator.ne,
    OP_LT: operator.lt,
    OP_LTE: operator.le,
    OP_GT: operator.gt,
    OP_GTE: operator.ge,
    OP_CONTAINS: operator.contains,
}

def _eval_node(product: Product, node: dict) -> bool:
    """Recursively evaluate a filter tree node against a product."""
    op = node["op"].lower()

    if op in LOGICAL_OPS:
        conditions = node.get("conditions", [])
        if not conditions:
            raise ValueError(f"{op.upper()} node must have at least 1 condition")
        if op == OP_NOT:
            if len(conditions) != 1:
                raise ValueError(f"NOT node must have exactly 1 condition, got {len(conditions)}")
            return not _eval_node(product, conditions[0])
        if op == OP_AND:
            return all(_eval_node(product, child) for child in conditions)
        return any(_eval_node(product, child) for child in conditions)
    elif op in COMPARISON_OPS:
        field = node["field"].lower()
        if field not in _ALLOWED_FIELDS:
            raise ValueError(f"Invalid field: {field}")
        value = node["value"]
        product_value = getattr(product, field)

        if field == "category":
            product_value = product_value.lower()
            value = value.lower() if isinstance(value, str) else value

        cmp_func = _COMPARISON_FUNCS.get(op)
        if cmp_func is None:
            raise ValueError(f"Invalid operator: {op}")
        return cmp_func(product_value, value)
    else:
        raise ValueError(f"Invalid operator: {op}")


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
    products = _PRODUCTS

    if not filters:
        results = products
    else:
        try:
            filter_tree = json.loads(filters)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid filter JSON: {e}"}

        try:
            results = [p for p in products if _eval_node(p, filter_tree)]
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            return {"status": "error", "message": f"Invalid filter structure: {e}"}

    if not results:
        return {
            "status": "no_results",
            "message": "No products found matching your criteria.",
        }

    return {"status": "success", "products": [p.model_dump() for p in results]}
