"""Tests for search_products and _eval_node."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.search_products import search_products, _eval_node
from schemas.product import Product
from constants import MAX_FILTER_LENGTH


# ---- helpers ----------------------------------------------------------------

def _names(result: dict) -> set[str]:
    """Extract product names from a search_products result."""
    return {p["name"] for p in result.get("products", [])}


def _count(result: dict) -> int:
    """Count products in a search_products result."""
    return len(result.get("products", []))


# ---------------------------------------------------------------------------
# A. search_products — Input Handling
# ---------------------------------------------------------------------------
class TestSearchProducts:

    def test_a1_no_filters_empty_string(self):
        result = search_products("")
        assert result["status"] == "success"
        assert _count(result) == 13

    def test_a2_no_filters_default(self):
        result = search_products()
        assert result["status"] == "success"
        assert _count(result) == 13

    def test_a3_invalid_json(self):
        result = search_products("not json{")
        assert result["status"] == "error"
        assert "Invalid filter JSON" in result["message"]

    def test_a4_valid_filter_results_found(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "clothing"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) > 0

    def test_a5_valid_filter_no_results(self):
        f = json.dumps({"field": "price", "op": "gt", "value": 9999})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_a6_missing_op_key(self):
        f = json.dumps({"field": "name", "value": "x"})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_a7_missing_field_key(self):
        f = json.dumps({"op": "eq", "value": "x"})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_a8_missing_value_key(self):
        f = json.dumps({"op": "eq", "field": "name"})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_a9_missing_conditions_in_logical_node(self):
        f = json.dumps({"op": "and"})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_a10_null_value_in_filter(self):
        f = json.dumps({"field": "name", "op": "contains", "value": None})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_a11_filter_at_max_length(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "clothing"})
        f = f.ljust(MAX_FILTER_LENGTH)
        assert len(f) == MAX_FILTER_LENGTH
        result = search_products(f)
        # Padded JSON is still valid JSON; just verify no length error
        assert result["status"] != "error" or "maximum length" not in result["message"]

    def test_a12_filter_exceeds_max_length(self):
        f = "x" * (MAX_FILTER_LENGTH + 1)
        result = search_products(f)
        assert result["status"] == "error"
        assert "maximum length" in result["message"]


# ---------------------------------------------------------------------------
# B. Comparison Operators on price (numeric)
# ---------------------------------------------------------------------------
class TestEvalNodeComparison:

    # -- price ---------------------------------------------------------------

    def test_b1_eq_exact_match(self):
        f = json.dumps({"field": "price", "op": "eq", "value": 45})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"UBC Hoodie"}

    def test_b2_eq_no_match(self):
        f = json.dumps({"field": "price", "op": "eq", "value": 999})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_b3_ne(self):
        f = json.dumps({"field": "price", "op": "ne", "value": 45})
        result = search_products(f)
        assert result["status"] == "success"
        assert "UBC Hoodie" not in _names(result)
        assert _count(result) == 12

    def test_b4_lt(self):
        f = json.dumps({"field": "price", "op": "lt", "value": 5})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Whole Wheat Bread", "Organic Apples"}

    def test_b5_lte(self):
        f = json.dumps({"field": "price", "op": "lte", "value": 4})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Whole Wheat Bread", "Organic Apples"}

    def test_b6_gt(self):
        f = json.dumps({"field": "price", "op": "gt", "value": 200})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"MacBook Air", "Smartwatch"}

    def test_b7_gte(self):
        f = json.dumps({"field": "price", "op": "gte", "value": 249})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"MacBook Air", "Smartwatch"}

    def test_b8_lt_boundary_no_match(self):
        f = json.dumps({"field": "price", "op": "lt", "value": 3})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_b9_lte_boundary(self):
        f = json.dumps({"field": "price", "op": "lte", "value": 3})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Whole Wheat Bread"}

    def test_b10_gt_boundary_no_match(self):
        f = json.dumps({"field": "price", "op": "gt", "value": 1299})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_b11_gte_boundary(self):
        f = json.dumps({"field": "price", "op": "gte", "value": 1299})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"MacBook Air"}

    # -- category (case-insensitive) -----------------------------------------

    def test_c1_eq_lowercase(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "clothing"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 4

    def test_c2_eq_uppercase_value(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "CLOTHING"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 4

    def test_c3_eq_mixed_case_value(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "Electronics"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 4

    def test_c4_ne(self):
        f = json.dumps({"field": "category", "op": "ne", "value": "groceries"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 9

    def test_c5_contains_substring(self):
        f = json.dumps({"field": "category", "op": "contains", "value": "cloth"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 4

    def test_c6_eq_nonexistent_category(self):
        f = json.dumps({"field": "category", "op": "eq", "value": "toys"})
        result = search_products(f)
        assert result["status"] == "no_results"

    # -- name ----------------------------------------------------------------

    def test_d1_eq_exact_match(self):
        f = json.dumps({"field": "name", "op": "eq", "value": "T-Shirt"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"T-Shirt"}

    def test_d2_eq_wrong_case(self):
        f = json.dumps({"field": "name", "op": "eq", "value": "t-shirt"})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_d3_contains_substring(self):
        f = json.dumps({"field": "name", "op": "contains", "value": "Shoe"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Running Shoes"}

    def test_d4_contains_case_sensitive(self):
        f = json.dumps({"field": "name", "op": "contains", "value": "shoe"})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_d5_contains_empty_string(self):
        f = json.dumps({"field": "name", "op": "contains", "value": ""})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 13

    def test_d6_ne(self):
        f = json.dumps({"field": "name", "op": "ne", "value": "T-Shirt"})
        result = search_products(f)
        assert result["status"] == "success"
        assert "T-Shirt" not in _names(result)
        assert _count(result) == 12


# ---------------------------------------------------------------------------
# E. Logical Operators
# ---------------------------------------------------------------------------
class TestEvalNodeLogical:

    def test_e1_and_two_conditions(self):
        f = json.dumps({
            "op": "and",
            "conditions": [
                {"field": "category", "op": "eq", "value": "clothing"},
                {"field": "price", "op": "lt", "value": 50},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"T-Shirt", "UBC Hoodie"}

    def test_e2_or_two_conditions(self):
        f = json.dumps({
            "op": "or",
            "conditions": [
                {"field": "category", "op": "eq", "value": "electronics"},
                {"field": "category", "op": "eq", "value": "accessories"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 5  # 4 electronics + 1 accessories

    def test_e3_not_single_condition(self):
        f = json.dumps({
            "op": "not",
            "conditions": [
                {"field": "category", "op": "eq", "value": "clothing"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 9

    def test_e4_and_all_false(self):
        f = json.dumps({
            "op": "and",
            "conditions": [
                {"field": "category", "op": "eq", "value": "clothing"},
                {"field": "price", "op": "gt", "value": 9999},
            ],
        })
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_e5_or_all_false(self):
        f = json.dumps({
            "op": "or",
            "conditions": [
                {"field": "price", "op": "gt", "value": 9999},
                {"field": "name", "op": "eq", "value": "nonexistent"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_e6_and_single_condition(self):
        f = json.dumps({
            "op": "and",
            "conditions": [
                {"field": "price", "op": "lt", "value": 5},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Whole Wheat Bread", "Organic Apples"}

    def test_e7_or_single_condition(self):
        f = json.dumps({
            "op": "or",
            "conditions": [
                {"field": "price", "op": "lt", "value": 5},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"Whole Wheat Bread", "Organic Apples"}

    # -- F. Case insensitivity of operators & fields -------------------------

    def test_f1_uppercase_op(self):
        f = json.dumps({"field": "price", "op": "EQ", "value": 45})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"UBC Hoodie"}

    def test_f2_mixed_case_op(self):
        f = json.dumps({"field": "price", "op": "Eq", "value": 45})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"UBC Hoodie"}

    def test_f3_uppercase_logical_op(self):
        f = json.dumps({
            "op": "AND",
            "conditions": [
                {"field": "price", "op": "gte", "value": 45},
                {"field": "category", "op": "eq", "value": "clothing"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert "UBC Hoodie" in _names(result)

    def test_f4_uppercase_field(self):
        f = json.dumps({"field": "PRICE", "op": "eq", "value": 45})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"UBC Hoodie"}

    def test_f5_mixed_case_field(self):
        f = json.dumps({"field": "Name", "op": "eq", "value": "T-Shirt"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"T-Shirt"}


# ---------------------------------------------------------------------------
# G. Nested / Complex Trees
# ---------------------------------------------------------------------------
class TestEvalNodeNested:

    def test_g1_three_level_nesting(self):
        """AND(OR(cat=clothing, cat=accessories), NOT(price gt 50))"""
        f = json.dumps({
            "op": "and",
            "conditions": [
                {
                    "op": "or",
                    "conditions": [
                        {"field": "category", "op": "eq", "value": "clothing"},
                        {"field": "category", "op": "eq", "value": "accessories"},
                    ],
                },
                {
                    "op": "not",
                    "conditions": [
                        {"field": "price", "op": "gt", "value": 50},
                    ],
                },
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        # clothing/accessories with price <= 50
        assert _names(result) == {"UBC Hoodie", "T-Shirt", "Backpack"}

    def test_g2_double_negation(self):
        """NOT(NOT(category eq clothing)) == category eq clothing"""
        f = json.dumps({
            "op": "not",
            "conditions": [{
                "op": "not",
                "conditions": [
                    {"field": "category", "op": "eq", "value": "clothing"},
                ],
            }],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 4

    def test_g3_and_three_conditions(self):
        """AND(cat=clothing, price gt 10, name contains 'Shirt')"""
        f = json.dumps({
            "op": "and",
            "conditions": [
                {"field": "category", "op": "eq", "value": "clothing"},
                {"field": "price", "op": "gt", "value": 10},
                {"field": "name", "op": "contains", "value": "Shirt"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _names(result) == {"T-Shirt"}

    def test_g4_or_three_conditions(self):
        """OR(cat=clothing, cat=electronics, cat=groceries) — all except accessories"""
        f = json.dumps({
            "op": "or",
            "conditions": [
                {"field": "category", "op": "eq", "value": "clothing"},
                {"field": "category", "op": "eq", "value": "electronics"},
                {"field": "category", "op": "eq", "value": "groceries"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 12

    def test_g5_deeply_nested_four_levels(self):
        """AND(OR(AND(price>5, price<100), cat=electronics), name ne 'Smartwatch')"""
        f = json.dumps({
            "op": "and",
            "conditions": [
                {
                    "op": "or",
                    "conditions": [
                        {
                            "op": "and",
                            "conditions": [
                                {"field": "price", "op": "gt", "value": 5},
                                {"field": "price", "op": "lt", "value": 100},
                            ],
                        },
                        {"field": "category", "op": "eq", "value": "electronics"},
                    ],
                },
                {"field": "name", "op": "ne", "value": "Smartwatch"},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        expected = {
            "UBC Hoodie", "MacBook Air", "Bluetooth Headphones",
            "USB-C Hub", "Running Shoes", "Backpack", "T-Shirt",
            "Denim Jacket", "Brown Rice",
        }
        assert _names(result) == expected

    def test_g6_docstring_example_filter(self):
        """The full example from the search_products docstring."""
        f = json.dumps({
            "op": "AND",
            "conditions": [
                {"op": "OR", "conditions": [
                    {"field": "category", "op": "eq", "value": "clothing"},
                    {"field": "category", "op": "eq", "value": "accessories"},
                ]},
                {"op": "OR", "conditions": [
                    {"field": "price", "op": "lt", "value": 10},
                    {"field": "price", "op": "gt", "value": 40},
                ]},
                {"op": "NOT", "conditions": [
                    {"field": "name", "op": "contains", "value": "jacket"},
                ]},
            ],
        })
        result = search_products(f)
        assert result["status"] == "success"
        # "jacket" is lowercase; "Denim Jacket" has uppercase J — case-sensitive
        # so Denim Jacket passes the NOT filter
        expected = {"UBC Hoodie", "Running Shoes", "Backpack", "Denim Jacket"}
        assert _names(result) == expected


# ---------------------------------------------------------------------------
# H. Error Cases — _eval_node direct
# ---------------------------------------------------------------------------
class TestEvalNodeErrors:

    @pytest.fixture()
    def product(self):
        return Product(
            id=0, name="Test", category="clothing",
            description="desc", price=10.0, image="img.png",
        )

    def test_h1_invalid_field_description(self, product):
        with pytest.raises(ValueError, match="Invalid field: description"):
            _eval_node(product, {"field": "description", "op": "eq", "value": "x"})

    def test_h2_invalid_field_id(self, product):
        with pytest.raises(ValueError, match="Invalid field: id"):
            _eval_node(product, {"field": "id", "op": "eq", "value": 0})

    def test_h3_invalid_field_image(self, product):
        with pytest.raises(ValueError, match="Invalid field: image"):
            _eval_node(product, {"field": "image", "op": "eq", "value": "x"})

    def test_h4_invalid_comparison_op(self, product):
        with pytest.raises(ValueError, match="Invalid operator: like"):
            _eval_node(product, {"field": "name", "op": "like", "value": "x"})

    def test_h5_invalid_logical_op(self, product):
        with pytest.raises(ValueError, match="Invalid operator: xor"):
            _eval_node(product, {"op": "xor", "conditions": []})

    def test_h6_not_zero_conditions(self, product):
        with pytest.raises(ValueError, match="NOT node must have at least 1 condition"):
            _eval_node(product, {"op": "not", "conditions": []})

    def test_h7_not_two_conditions(self, product):
        with pytest.raises(
            ValueError,
            match=r"NOT node must have exactly 1 condition, got 2",
        ):
            _eval_node(product, {
                "op": "not",
                "conditions": [
                    {"field": "name", "op": "eq", "value": "a"},
                    {"field": "name", "op": "eq", "value": "b"},
                ],
            })

    def test_h8_and_zero_conditions(self, product):
        with pytest.raises(ValueError, match="AND node must have at least 1 condition"):
            _eval_node(product, {"op": "and", "conditions": []})

    def test_h9_or_zero_conditions(self, product):
        with pytest.raises(ValueError, match="OR node must have at least 1 condition"):
            _eval_node(product, {"op": "or", "conditions": []})


# ---------------------------------------------------------------------------
# I. Type Mismatch / Boundary Cases
# ---------------------------------------------------------------------------
class TestEvalNodeEdgeCases:

    def test_i1_string_comparison_on_price(self):
        # Python 3: eq across types returns False (no TypeError)
        f = json.dumps({"field": "price", "op": "eq", "value": "45"})
        result = search_products(f)
        assert result["status"] == "no_results"

    def test_i2_numeric_comparison_on_name(self):
        # str > int raises TypeError
        f = json.dumps({"field": "name", "op": "gt", "value": 100})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_i3_contains_on_price(self):
        # float doesn't support __contains__
        f = json.dumps({"field": "price", "op": "contains", "value": 4})
        result = search_products(f)
        assert result["status"] == "error"
        assert "Invalid filter structure" in result["message"]

    def test_i4_lt_on_category(self):
        # String comparison: "accessories" < "d" and "clothing" < "d" are True
        f = json.dumps({"field": "category", "op": "lt", "value": "d"})
        result = search_products(f)
        assert result["status"] == "success"
        assert _count(result) == 5  # 4 clothing + 1 accessories

    def test_i5_int_vs_float_price(self):
        f_int = json.dumps({"field": "price", "op": "eq", "value": 45})
        f_float = json.dumps({"field": "price", "op": "eq", "value": 45.0})
        result_int = search_products(f_int)
        result_float = search_products(f_float)
        assert result_int["status"] == "success"
        assert result_float["status"] == "success"
        assert _names(result_int) == _names(result_float) == {"UBC Hoodie"}
