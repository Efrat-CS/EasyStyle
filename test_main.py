"""Unit tests for main.py helper functions."""

import sys
from unittest.mock import MagicMock

# Mock third-party imports before main.py loads (keeps tests lightweight).
_mock_st = MagicMock()
_mock_st.secrets = {
    "RAPIDAPI_KEY": "test-key",
    "ASOS_HOST": "asos2.p.rapidapi.com",
    "SHEIN_HOST": "shein-data-api.p.rapidapi.com",
    "HM_HOST": "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com",
}
_mock_urllib3 = MagicMock()
_mock_urllib3.disable_warnings = MagicMock()
_mock_urllib3.exceptions = MagicMock()

sys.modules.setdefault("streamlit", _mock_st)
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("urllib3", _mock_urllib3)

from main import build_smart_query, convert_to_ils, deduplicate


# ---------------------------------------------------------------------------
# build_smart_query
# ---------------------------------------------------------------------------

def test_build_smart_query_dress_with_color_and_skirt_length():
    """Dress category should include color, skirt length, and normalized category."""
    prefs = {
        "favorite_colors": ["black"],
        "skirt_length": ["maxi"],
        "sleeve_length": ["long"],
    }
    result = build_smart_query("Dresses", prefs)
    assert result == "black maxi dress"


def test_build_smart_query_top_with_long_sleeves():
    """Tops/shirts should map sleeve preference to a readable phrase."""
    prefs = {
        "favorite_colors": ["white"],
        "sleeve_length": ["long"],
    }
    result = build_smart_query("Tops/Shirts (Women)", prefs)
    assert result == "white long sleeve top/shirt (women)"


def test_build_smart_query_top_with_short_sleeves():
    """Short sleeve preference should appear in the query."""
    prefs = {"favorite_colors": ["blue"], "sleeve_length": ["short"]}
    result = build_smart_query("Men's Shirts", prefs)
    assert result == "blue short sleeve men's shirt"


def test_build_smart_query_top_with_three_quarter_sleeves():
    """3/4 sleeve preference should be normalized in the query."""
    prefs = {"favorite_colors": ["red"], "sleeve_length": ["3/4"]}
    result = build_smart_query("Men's T-shirts", prefs)
    assert result == "red 3/4 sleeve men's t-shirts"


def test_build_smart_query_pants_category():
    """Non dress/shirt categories should only include color and category name."""
    prefs = {
        "favorite_colors": ["navy"],
        "skirt_length": ["mini"],
        "sleeve_length": ["short"],
    }
    result = build_smart_query("Men's Trousers", prefs)
    assert result == "navy men's pants"


def test_build_smart_query_empty_favorite_colors():
    """Empty favorite_colors must not crash and should omit the color segment."""
    prefs = {
        "favorite_colors": [],
        "skirt_length": ["midi"],
    }
    result = build_smart_query("Skirts", prefs)
    assert result == "midi skirt"


def test_build_smart_query_missing_optional_prefs():
    """Missing preference keys should still produce a valid category-only query."""
    result = build_smart_query("Women's Shoes", {})
    assert result == "women's shoes"


# ---------------------------------------------------------------------------
# convert_to_ils
# ---------------------------------------------------------------------------

def test_convert_to_ils_gbp():
    """British pounds should convert using the £ multiplier."""
    assert convert_to_ils("£50") == "₪235"


def test_convert_to_ils_usd():
    """US dollars should convert using the $ multiplier."""
    assert convert_to_ils("$100") == "₪370"


def test_convert_to_ils_eur():
    """Euros should convert using the € multiplier."""
    assert convert_to_ils("€25") == "₪100"


def test_convert_to_ils_plain_number():
    """Numeric strings without a currency symbol should round as ILS."""
    assert convert_to_ils("120") == "₪120"


def test_convert_to_ils_na_literal():
    """The literal 'N/A' should pass through unchanged."""
    assert convert_to_ils("N/A") == "N/A"


def test_convert_to_ils_empty_string():
    """Empty input should return 'N/A' without raising."""
    assert convert_to_ils("") == "N/A"


def test_convert_to_ils_none():
    """Falsy None input should return 'N/A' without raising."""
    assert convert_to_ils(None) == "N/A"


def test_convert_to_ils_invalid_string():
    """Non-numeric strings should be returned as-is when parsing fails."""
    assert convert_to_ils("N/A-ish") == "N/A-ish"
    assert convert_to_ils("free") == "free"


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

def _product(name, product_id="1"):
    return {"id": product_id, "name": name}


def test_deduplicate_case_insensitive():
    """Duplicate names differing only by case should keep the first item."""
    products = [
        _product("Summer Dress", "1"),
        _product("summer dress", "2"),
        _product("SUMMER DRESS", "3"),
    ]
    result = deduplicate(products)
    assert len(result) == 1
    assert result[0]["id"] == "1"


def test_deduplicate_keeps_distinct_names():
    """Products with different names should all be retained."""
    products = [_product("Dress", "1"), _product("Skirt", "2")]
    result = deduplicate(products)
    assert len(result) == 2
    assert [p["name"] for p in result] == ["Dress", "Skirt"]


def test_deduplicate_empty_list():
    """An empty product list should return an empty list."""
    assert deduplicate([]) == []


def test_deduplicate_preserves_order():
    """First occurrence of each unique name should determine output order."""
    products = [
        _product("Alpha", "1"),
        _product("Beta", "2"),
        _product("alpha", "3"),
    ]
    result = deduplicate(products)
    assert [p["id"] for p in result] == ["1", "2"]
