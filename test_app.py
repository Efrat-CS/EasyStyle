"""Unit tests for app.py helper functions."""

import sys
from unittest.mock import MagicMock, mock_open, patch

# ---------------------------------------------------------------------------
# Mock third-party imports before app.py (and main.py) load.
# ---------------------------------------------------------------------------
_mock_st = MagicMock()
_mock_st.secrets = MagicMock()
_mock_st.secrets.get.return_value = None
_mock_st.session_state = MagicMock()

_mock_sidebar = MagicMock()
_mock_sidebar.__enter__ = MagicMock(return_value=_mock_sidebar)
_mock_sidebar.__exit__ = MagicMock(return_value=False)
_mock_st.sidebar = _mock_sidebar

def _selectbox_side_effect(label, options, **kwargs):
    if label == "Gender":
        return "Female"
    if label == "Pants Length":
        return "both"
    if label == "Category" and options:
        return options[0]
    index = kwargs.get("index", 0)
    return options[index] if options else ""


def _radio_side_effect(label, options, **kwargs):
    if label == "Go to:":
        return "Shop"
    if label == "Logic":
        return "Smart (High Recall)"
    return options[0] if options else ""


_mock_st.text_input.side_effect = lambda label, **kwargs: {
    "Name": "Test User",
    "Favorite Colors": "",
    "Style Keywords": "",
}.get(label, kwargs.get("value", ""))

_mock_st.selectbox.side_effect = _selectbox_side_effect
_mock_st.radio.side_effect = _radio_side_effect
_mock_st.number_input.return_value = 1
_mock_st.slider.return_value = (50, 600)
_mock_st.multiselect.return_value = []

_mock_components = MagicMock()
_mock_urllib3 = MagicMock()
_mock_urllib3.disable_warnings = MagicMock()
_mock_urllib3.exceptions = MagicMock()

sys.modules["streamlit"] = _mock_st
sys.modules["streamlit.components.v1"] = _mock_components
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("urllib3", _mock_urllib3)

from app import _parse_price, save_to_favorites


# ---------------------------------------------------------------------------
# _parse_price
# ---------------------------------------------------------------------------

def _product_with_price(text):
    return {"price": {"current": {"text": text}}}


def test_parse_price_clean_ils_string():
    """A simple ₪ price string should extract the numeric value."""
    assert _parse_price(_product_with_price("₪150")) == 150.0


def test_parse_price_with_comma_separator():
    """Commas in formatted prices should be stripped before parsing."""
    assert _parse_price(_product_with_price("₪1,200")) == 1200.0


def test_parse_price_messy_string():
    """Extra label text around the number should not block extraction."""
    assert _parse_price(_product_with_price("Now only ₪99.99!")) == 99.99


def test_parse_price_decimal_value():
    """Decimal amounts should be preserved as floats."""
    assert _parse_price(_product_with_price("₪49.50")) == 49.50


def test_parse_price_empty_text():
    """Missing or empty price text should return None."""
    assert _parse_price(_product_with_price("")) is None


def test_parse_price_missing_structure():
    """Products without a price block should return None safely."""
    assert _parse_price({}) is None
    assert _parse_price({"price": {}}) is None


def test_parse_price_non_numeric_text():
    """Non-numeric price strings should return None."""
    assert _parse_price(_product_with_price("N/A")) is None


# ---------------------------------------------------------------------------
# save_to_favorites
# ---------------------------------------------------------------------------

def _sample_product(product_id="asos_999", store="ASOS"):
    return {
        "id": product_id,
        "name": "Floral Midi Dress",
        "store": store,
        "price": {"current": {"text": "₪180"}},
        "imageUrl": "https://example.com/dress.jpg",
    }


def test_save_to_favorites_new_product():
    """A new product should be appended and persisted via json.dump."""
    product = _sample_product()

    with patch("app.load_favorites", return_value=[]):
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_dump:
                result = save_to_favorites(product)

    assert result is True
    mock_file.assert_called_once_with("favorites.json", "w", encoding="utf-8")
    mock_dump.assert_called_once()

    saved_list = mock_dump.call_args[0][0]
    assert len(saved_list) == 1
    assert saved_list[0]["id"] == product["id"]
    assert saved_list[0]["name"] == product["name"]
    assert saved_list[0]["price"] == "₪180"
    assert saved_list[0]["store"] == "ASOS"
    assert saved_list[0]["link"] == "https://www.asos.com/prd/999"


def test_save_to_favorites_duplicate_prevention():
    """An existing product id should be rejected without writing to disk."""
    product = _sample_product()
    existing = [{
        "id": product["id"],
        "name": product["name"],
        "price": "₪180",
        "link": "https://www.asos.com/prd/999",
        "store": "ASOS",
        "imageUrl": "",
    }]

    with patch("app.load_favorites", return_value=existing):
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_dump:
                result = save_to_favorites(product)

    assert result is False
    mock_file.assert_not_called()
    mock_dump.assert_not_called()


def test_save_to_favorites_shein_link_format():
    """SHEIN products should generate a keyword search link."""
    product = _sample_product(product_id="shein_42", store="SHEIN")

    with patch("app.load_favorites", return_value=[]):
        with patch("builtins.open", mock_open()):
            with patch("json.dump") as mock_dump:
                save_to_favorites(product)

    saved = mock_dump.call_args[0][0][0]
    assert "shein.com/search?keyword=Floral%20Midi%20Dress" in saved["link"]
