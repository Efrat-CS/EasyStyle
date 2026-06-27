# =========================
# app.py
# =========================

import streamlit as st
import streamlit.components.v1 as components
import os
import json
import html
import urllib3
#from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#load_dotenv()

FAVORITES_FILE = "favorites.json"
PROFILE_FILE = "user_profile.json"

from main import (
    ASOS_CATEGORIES,
    STORE_OPTIONS,
    get_all_products,
    get_storefront_products,
    load_profile,
    save_profile
)

# =========================
# Favorites helpers
# =========================
def load_favorites():

    if os.path.exists(FAVORITES_FILE):

        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def save_to_favorites(product):

    favorites = load_favorites()

    if any(fav["id"] == product["id"] for fav in favorites):
        return False

    store = product.get("store", "ASOS").upper()
    link = get_product_link(product)

    favorites.append({
        "name": product["name"],
        "price": product.get("price", {}).get("current", {}).get("text", "N/A"),
        "link": link,
        "id": product["id"],
        "store": store,
        "imageUrl": product.get("imageUrl", "")
    })

    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:

        json.dump(
            favorites,
            f,
            indent=4,
            ensure_ascii=False
        )

    return True


def get_product_link(item):
    if item.get("url"):
        return item["url"]

    raw_id = str(item["id"]).split("_")[-1]
    store = item.get("store", "ASOS").upper()

    if store == "HM":
        return (
            "https://www2.hm.com/en_us/"
            f"search-results.html?q={item['name'].replace(' ', '+')}"
        )
    if store == "SHEIN":
        return (
            "https://www.shein.com/"
            f"search?keyword={item['name'].replace(' ', '%20')}"
        )
    return f"https://www.asos.com/prd/{raw_id}"


def normalize_image_url(img):
    if not img:
        return ""
    if img.startswith("//"):
        return "https:" + img
    if not img.startswith("http"):
        return "https://" + img
    return img


def is_favorited(product_id):
    return any(fav["id"] == product_id for fav in load_favorites())


def inject_card_styles():
    st.html(
        """
        <style>
        :root {
            --ink: #080808;
            --muted: #6f6f6f;
            --line: #e8e5df;
            --paper: #ffffff;
            --soft: #f6f4f0;
        }
        html, body, .stApp {
            background: var(--paper) !important;
            color: var(--ink) !important;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif !important;
            letter-spacing: 0 !important;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"], footer {
            display: none !important;
        }
        .block-container {
            max-width: 1680px !important;
            padding: 0 28px 56px !important;
        }
        .site-nav {
            position: sticky;
            top: 0;
            z-index: 999;
            height: 74px;
            display: grid;
            grid-template-columns: minmax(280px, 1fr) auto minmax(280px, 1fr);
            align-items: center;
            padding: 0 30px;
            background: rgba(255, 255, 255, 0.94);
            border-bottom: 1px solid rgba(8, 8, 8, 0.08);
            backdrop-filter: blur(16px);
        }
        .site-nav-spacer {
            height: 24px;
        }
        .site-logo {
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2.2rem, 4.6vw, 4.2rem);
            line-height: 1;
            font-weight: 500;
            letter-spacing: 0.04em;
            color: var(--ink);
            white-space: nowrap;
        }
        .site-nav-left,
        .site-nav-right {
            display: flex;
            align-items: center;
            gap: 22px;
            min-width: 0;
        }
        .site-nav-right {
            justify-content: flex-end;
        }
        .nav-link,
        .signin-button {
            font-size: 0.72rem;
            font-weight: 500;
            color: var(--ink);
            background: transparent;
            border: 0;
            padding: 0;
            letter-spacing: 0.04em;
            white-space: nowrap;
            text-decoration: none;
        }
        .signin-button {
            border-bottom: 1px solid var(--ink);
            cursor: pointer;
        }
        .site-logo,
        .site-logo:visited,
        .nav-link:visited,
        .signin-button:visited {
            color: var(--ink);
            text-decoration: none;
        }
        .editorial-hero {
            min-height: 34vh;
            display: grid;
            align-content: end;
            padding: 5vh 0 28px;
            border-bottom: 1px solid var(--line);
            margin-bottom: 30px;
        }
        .editorial-kicker {
            margin: 0 0 12px;
            font-size: 0.72rem;
            font-weight: 500;
            color: var(--muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .editorial-title {
            max-width: 980px;
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(3rem, 8vw, 9rem);
            line-height: 0.9;
            font-weight: 400;
            color: var(--ink);
        }
        .editorial-row {
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 24px;
            margin: 0 0 16px;
        }
        .section-title {
            margin: 0;
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .section-note {
            margin: 0;
            font-size: 0.76rem;
            color: var(--muted);
        }
        .signin-panel {
            max-width: 520px;
            padding: 8px 0 60px;
        }
        .signin-copy {
            margin: 0 0 28px;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }
        .celune-loading {
            min-height: 34vh;
            display: grid;
            place-items: center;
            padding: 52px 0;
        }
        .celune-loading-inner {
            width: min(360px, 70vw);
            text-align: center;
        }
        .celune-loading-logo {
            margin: 0 0 22px;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2.2rem, 6vw, 4.6rem);
            line-height: 1;
            font-weight: 400;
            color: var(--ink);
        }
        .celune-loading-line {
            position: relative;
            height: 1px;
            overflow: hidden;
            background: var(--line);
        }
        .celune-loading-line::after {
            content: "";
            position: absolute;
            inset: 0;
            width: 42%;
            background: var(--ink);
            animation: celune-load 1.25s cubic-bezier(0.65, 0, 0.35, 1) infinite;
        }
        .celune-loading-text {
            margin: 16px 0 0;
            font-size: 0.66rem;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--muted);
        }
        @keyframes celune-load {
            0% {
                transform: translateX(-120%);
            }
            100% {
                transform: translateX(260%);
            }
        }
        div[data-testid="stSidebar"] {
            background: #fbfaf7 !important;
            border-right: 1px solid var(--line);
        }
        div[data-testid="stSidebar"] h2,
        div[data-testid="stSidebar"] h3 {
            font-size: 0.74rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 500 !important;
        }
        div[data-testid="stSidebar"] label,
        div[data-testid="stSidebar"] p {
            font-size: 0.78rem !important;
        }
        .stButton button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 0 !important;
            border: 1px solid var(--ink) !important;
            background: var(--ink) !important;
            color: white !important;
            min-height: 44px !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            box-shadow: none !important;
        }
        .stSelectbox div,
        .stMultiSelect div,
        .stTextInput input,
        .stNumberInput input {
            border-radius: 0 !important;
        }
        div[data-testid="stAlert"] {
            border-radius: 0 !important;
            border: 1px solid var(--line) !important;
            background: #fbfaf7 !important;
            color: var(--ink) !important;
        }
        .product-card {
            background: transparent;
            border: 0;
            border-radius: 0;
            overflow: hidden;
            margin-bottom: 0;
        }
        .product-card-media {
            position: relative;
            background: var(--soft);
            overflow: hidden;
        }
        .product-card-image {
            width: 100%;
            aspect-ratio: 2 / 3;
            object-fit: cover;
            display: block;
            transition: transform 0.35s ease;
        }
        .product-card-media:hover .product-card-image {
            transform: scale(1.025);
        }
        .product-card-open {
            position: absolute;
            inset: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
            border-radius: 0;
            border: 0;
            background: rgba(255, 255, 255, 0.02);
            color: transparent;
            text-decoration: none;
            opacity: 1;
            pointer-events: auto;
        }
        .product-card-open::before {
            content: "";
        }
        .product-card-open svg {
            display: none;
        }
        .product-card-star {
            position: absolute;
            top: 8px;
            left: 8px;
            background: rgba(255, 255, 255, 0.88);
            border-radius: 0;
            padding: 5px 8px;
            font-size: 0.62rem;
            font-weight: 500;
            color: var(--ink);
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .product-card-body {
            padding: 10px 0 4px;
        }
        .product-card-name {
            margin: 0;
            font-size: 0.78rem;
            font-weight: 400;
            line-height: 1.35;
            color: var(--ink);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.1rem;
            text-transform: uppercase;
        }
        .product-card-store {
            margin: 4px 0 0;
            font-size: 0.64rem;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }
        .product-card-price {
            margin: 0;
            padding-top: 0;
            font-size: 0.76rem;
            font-weight: 400;
            color: var(--ink);
            letter-spacing: 0;
        }
        div[data-testid="stVerticalBlock"] > div:has(.product-card) {
            gap: 0.1rem;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) button {
            width: 34px !important;
            min-width: 34px !important;
            height: 34px !important;
            padding: 0 !important;
            border-radius: 0 !important;
            border: 0 !important;
            background: transparent !important;
            color: var(--ink) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1rem !important;
            line-height: 1 !important;
            box-shadow: none !important;
            min-height: 34px !important;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) button > div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 100% !important;
            line-height: 1 !important;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) button p {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 0 1px !important;
            line-height: 1 !important;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) button:hover {
            background: transparent !important;
            color: var(--muted) !important;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) {
            align-items: center;
            padding: 0 0 22px;
            border: 0;
            border-radius: 0;
            margin-top: 0;
            margin-bottom: 0.4rem;
            background: transparent;
            box-shadow: none;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) > div {
            display: flex;
            align-items: center;
        }
        @media (max-width: 760px) {
            .block-container {
                padding: 0 14px 40px !important;
            }
            .site-nav {
                grid-template-columns: auto 1fr auto;
                height: 62px;
                padding: 0 14px;
            }
            .site-logo {
                font-size: 1.7rem;
                justify-self: center;
            }
            .site-nav-left .nav-link:not(:first-child),
            .site-nav-right .nav-link {
                display: none;
            }
            .site-nav-left,
            .site-nav-right {
                gap: 12px;
            }
            .editorial-hero {
                min-height: 26vh;
            }
        }
        </style>
        """
    )


ICON_EXTERNAL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>'
    "</svg>"
)


# =========================
# Streamlit setup
# =========================
st.set_page_config(
    page_title="Célune",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =========================
# Google Analytics Setup
# =========================
ga_id = st.secrets.get("GA_MEASUREMENT_ID")
if ga_id:
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>
    """
    
    components.html(ga_code, height=0)

inject_card_styles()


PAGE_OPTIONS = ["Home", "Shop", "Favorites", "Sign In"]

COLLECTIONS = {
    "Woman": {
        "category_key": "1",
        "title": "New silhouettes",
        "note": "A live edit from Zara, H&M, ASOS and more.",
        "kicker": "Woman collection",
    },
    "Man": {
        "category_key": "7",
        "title": "Sharp layers",
        "note": "Clean shirts, relaxed tailoring, and daily essentials.",
        "kicker": "Man collection",
    },
    "Shoes": {
        "category_key": "5",
        "title": "Groundwork",
        "note": "Minimal shoes and statement finishes for the full look.",
        "kicker": "Shoe edit",
    },
}


def query_value(key, default):
    value = st.query_params.get(key, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value or default


def requested_page():
    page_name = query_value("page", "Home")
    page_name = "Sign In" if page_name in {"SignIn", "signin"} else page_name
    return page_name if page_name in PAGE_OPTIONS else "Home"


def requested_collection():
    collection = query_value("collection", "Woman")
    return collection if collection in COLLECTIONS else "Woman"


def render_top_nav():
    st.html(
        """
        <header class="site-nav">
            <div class="site-nav-left">
                <a class="nav-link" href="?page=Shop">MENU</a>
                <a class="nav-link" href="?page=Home&collection=Woman">WOMAN</a>
                <a class="nav-link" href="?page=Home&collection=Man">MAN</a>
                <a class="nav-link" href="?page=Home&collection=Shoes">SHOES</a>
            </div>
            <a class="site-logo" href="?page=Home&collection=Woman">Célune</a>
            <div class="site-nav-right">
                <a class="nav-link" href="?page=Shop">SEARCH</a>
                <a class="nav-link" href="?page=Favorites">FAVORITES</a>
                <a class="signin-button" href="?page=Sign%20In">SIGN IN</a>
            </div>
        </header>
        <div class="site-nav-spacer"></div>
        """
    )


render_top_nav()


# =========================
# Session state
# =========================
if "user_name" not in st.session_state:

    st.session_state.user_name = ""
    st.session_state.gender = "Select..."

    prof = load_profile()

    if prof:
        st.session_state.user_name = prof.get("name", "")
        st.session_state.gender = prof.get("gender", "Select...")


# =========================
# Sidebar
# =========================
with st.sidebar:

    st.header("Navigation")

    initial_page = requested_page()
    sidebar_page = st.radio(
        "Go to:",
        PAGE_OPTIONS,
        index=PAGE_OPTIONS.index(initial_page),
        key=f"sidebar_page_{initial_page}"
    )
    page = initial_page if "page" in st.query_params else sidebar_page

    st.divider()

    st.header("Profile")

    u_name = st.text_input(
        "Name",
        value=st.session_state.user_name,
        placeholder="Enter your name..."
    )

    gender_options = [
        "Select...",
        "Female",
        "Male",
        "Other"
    ]

    idx = (
        gender_options.index(st.session_state.gender)
        if st.session_state.gender in gender_options
        else 0
    )

    u_gender = st.selectbox(
        "Gender",
        gender_options,
        index=idx
    )

    # Save profile
    if (
        u_name != st.session_state.user_name
        or u_gender != st.session_state.gender
    ):

        if u_name and u_gender != "Select...":

            curr = load_profile() or {}

            curr.update({
                "name": u_name,
                "gender": u_gender
            })

            save_profile(curr)

            st.session_state.user_name = u_name
            st.session_state.gender = u_gender

    st.divider()

    # =========================
    # Filters
    # =========================
    st.subheader("Pages")
    page_num = st.number_input("Page Number", min_value=1, value=1, step=1)

    st.subheader("Filter Mode")

    filter_mode = st.radio(
        "Logic",
        [
            "Smart (High Recall)",
            "Strict (Exact Name Match)"
        ]
    )

    st.subheader("Stores")

    selected_stores = st.multiselect(
        "Search in",
        STORE_OPTIONS,
        default=STORE_OPTIONS
    )

    st.subheader("Price Range")

    min_p, max_p = st.slider(
        "ILS",
        0,
        1500,
        (50, 600)
    )

    st.subheader("Lengths & Fit")

    sleeve_p = st.multiselect(
        "Sleeves",
        [
            "sleeveless",
            "short",
            "elbow",
            "3/4",
            "long",
            "extra_long"
        ]
    )

    skirt_p = st.multiselect(
        "Skirt/Dress Length",
        [
            "micro",
            "mini",
            "knee",
            "midi",
            "tea",
            "maxi",
            "floor"
        ]
    )

    pants_p = st.selectbox(
        "Pants Length",
        ["short", "long", "both"],
        index=2
    )

    fit_p = st.multiselect(
        "Fit",
        [
            "skinny",
            "slim",
            "regular",
            "relaxed",
            "oversized",
            "loose",
            "flare",
            "straight"
        ]
    )

    st.subheader("Shoes")

    shoe_p = st.multiselect(
        "Types",
        [
            "sneakers",
            "heels",
            "boots",
            "flats",
            "sandals",
            "loafers"
        ]
    )

    st.subheader("Style Notes")

    colors_t = st.text_input(
        "Favorite Colors"
    )

    style_t = st.text_input(
        "Style Keywords"
    )


# =========================
# Guard
# =========================
if not u_name:
    u_name = "Guest"

if u_gender == "Select...":
    u_gender = "Female"


# =========================
# User prefs
# =========================
favorite_colors = [
    c.strip().lower()
    for c in colors_t.split(",")
    if c.strip()
]

style_prefs = [
    s.strip().lower()
    for s in style_t.split(",")
    if s.strip()
]

user_prefs = {
    "favorite_colors": favorite_colors,
    "preferences": style_prefs,
    "sleeve_length": sleeve_p,
    "skirt_length": skirt_p,
    "pants_length": pants_p,
    "fit_style": fit_p,
    "shoe_types": shoe_p,
    "price_min": min_p,
    "price_max": max_p,
}


@st.cache_data(ttl=900, show_spinner=False)
def fetch_products_cached(cat_id, cat_name, prefs_json, offset):
    return get_all_products(
        cat_id,
        cat_name,
        json.loads(prefs_json),
        offset=offset
    )


@st.cache_data(ttl=900, show_spinner=False)
def fetch_storefront_products_cached(cat_id, cat_name, prefs_json, offset):
    return get_storefront_products(
        cat_id,
        cat_name,
        json.loads(prefs_json),
        offset=offset
    )


def sort_for_storefront(products):
    store_rank = {
        "ZARA": 0,
        "HM": 1,
        "ASOS": 2,
        "SHEIN": 3,
    }
    return sorted(
        products,
        key=lambda item: (
            store_rank.get(item.get("store", "").upper(), 9),
            item.get("name", "")
        )
    )


def render_collection_header(title, note, kicker="New edit"):
    safe_title = html.escape(title)
    safe_note = html.escape(note)
    safe_kicker = html.escape(kicker)
    st.html(
        f"""
        <section class="editorial-hero">
            <p class="editorial-kicker">{safe_kicker}</p>
            <h1 class="editorial-title">{safe_title}</h1>
        </section>
        <div class="editorial-row">
            <p class="section-title">{safe_title}</p>
            <p class="section-note">{safe_note}</p>
        </div>
        """
    )


def render_loading_state(placeholder, message="Curating selection"):
    safe_message = html.escape(message)
    placeholder.html(
        f"""
        <section class="celune-loading" aria-live="polite" aria-label="{safe_message}">
            <div class="celune-loading-inner">
                <p class="celune-loading-logo">Célune</p>
                <div class="celune-loading-line"></div>
                <p class="celune-loading-text">{safe_message}</p>
            </div>
        </section>
        """
    )


def render_product_grid(products, *, prefix, columns=4, limit=None):
    visible = [
        product
        for product in products
        if product.get("imageUrl") and product.get("name")
    ]

    if limit:
        visible = visible[:limit]

    cols = st.columns(columns)
    for idx, product in enumerate(visible):
        render_product_card(
            {"data": product, "star": False},
            idx,
            cols[idx % columns],
            prefix=prefix
        )

    return len(visible)


# =========================
# Filter helpers
# =========================
BAD_SKIRT_WORDS = [
    "mini",
    "micro"
]

BAD_SLEEVE_WORDS = [
    "sleeveless", "bandeau", "halter", "strapless", "strap", 
    "cami", "tank", "vest", "top", "neck", "cut out"
]

SKIRT_SYNONYMS = {
    "maxi": ["maxi", "floor", "full length"],
    "midi": ["midi", "midaxi"],
    "tea": ["tea length"],
    "knee": ["knee"],
    "mini": ["mini"],
    "micro": ["micro"]
}

SLEEVE_SYNONYMS = {
    "long": ["long sleeve", "long-sleeve"],
    "3/4": ["3/4", "three quarter"],
    "elbow": ["elbow"],
    "short": ["short sleeve"],
    "sleeveless": ["sleeveless"],
    "extra_long": ["bishop", "balloon sleeve"]
}

SHOE_SYNONYMS = {
    "sneakers": ["sneaker", "trainer"],
    "heels": ["heel", "pump"],
    "boots": ["boot"],
    "flats": ["flat"],
    "sandals": ["sandal"],
    "loafers": ["loafer"]
}

allow_short_skirts = any(s in (skirt_p or []) for s in ["micro", "mini", "knee"])
allow_short_sleeves = any(s in (sleeve_p or []) for s in ["sleeveless", "short"])


# =========================
# Match helper
# =========================
def _has_match(item_name, preference_list, synonyms_dict):

    for pref in preference_list:

        words = synonyms_dict.get(pref, [pref])

        if any(w in item_name for w in words):
            return True

    return False


# =========================
# Parse price
# =========================
def _parse_price(product):

    try:

        text = (
            product.get("price", {})
            .get("current", {})
            .get("text", "")
        )

        clean = "".join(
            c for c in text.replace(",", "")
            if c.isdigit() or c == "."
        )

        if clean:
            return float(clean)

    except:
        pass

    return None

# =========================
# Filtering
# =========================
def filter_products(products, sel_cat):
    matches = []

    for item in products:
        item_name = item.get("name", "").lower()

        # --- 1. סינון מחיר ---
        price_val = _parse_price(item)
        if price_val is not None:
            if price_val < min_p or price_val > max_p:
                continue

        # --- 2. לוגיקת סינון חכמה ---
        is_match = True
        
        # אם בחרת Smart - אנחנו רק פוסלים את מה שבוודאות לא מתאים (Negative Matching)
        if filter_mode == "Smart (High Recall)":
            if not allow_short_skirts and any(bad in item_name for bad in BAD_SKIRT_WORDS):
                is_match = False
            if is_match and not allow_short_sleeves and any(bad in item_name for bad in BAD_SLEEVE_WORDS):
                is_match = False
        
        # אם בחרת Strict - הפריט חייב להכיל את המילים שביקשת (Positive Matching)
        else:
            if ("Dresses" in sel_cat or "Skirts" in sel_cat) and skirt_p:
                if not _has_match(item_name, skirt_p, SKIRT_SYNONYMS):
                    is_match = False
            if is_match and ("Dresses" in sel_cat or "Tops" in sel_cat) and sleeve_p:
                if not _has_match(item_name, sleeve_p, SLEEVE_SYNONYMS):
                    is_match = False

        if not is_match:
            continue

        # --- 3. בונוס כוכב ---
        # פריט שגם עבר סינון וגם מכיל את המילים המדויקות שביקשת מקבל ⭐
        has_pos_match = False
        if skirt_p and _has_match(item_name, skirt_p, SKIRT_SYNONYMS):
            has_pos_match = True
        if sleeve_p and _has_match(item_name, sleeve_p, SLEEVE_SYNONYMS):
            has_pos_match = True

        is_star = has_pos_match or \
                  (any(c in item_name for c in favorite_colors) if favorite_colors else False) or \
                  (any(s in item_name for s in style_prefs) if style_prefs else False)

        matches.append({"data": item, "star": is_star})

    return matches

# =========================
# Product card
# =========================
def render_product_card(m_info, idx, col, *, prefix="shop"):
    item = m_info["data"]
    store = item.get("store", "ASOS").upper()
    img = normalize_image_url(item.get("imageUrl", ""))
    link = get_product_link(item)
    price_text = (
        item.get("price", {})
        .get("current", {})
        .get("text", "N/A")
    )
    saved = is_favorited(item["id"])
    safe_name = html.escape(item["name"])
    safe_store = html.escape(store)
    safe_price = html.escape(price_text)
    safe_img = html.escape(img)
    star_badge = (
        '<span class="product-card-star">Recommended</span>'
        if m_info.get("star")
        else ""
    )
    image_html = (
        f'<img src="{safe_img}" class="product-card-image" alt="{safe_name}">'
        if img
        else '<div class="product-card-image"></div>'
    )
    open_action_html = f"""
        <a href="{html.escape(link)}" target="_blank" rel="noopener noreferrer"
           class="product-card-open" title="Open on {safe_store}"
           aria-label="Open on {safe_store}">
            {ICON_EXTERNAL}
        </a>
    """

    with col:
        st.html(
            f"""
            <div class="product-card">
                <div class="product-card-media">
                    {image_html}
                    {star_badge}
                    {open_action_html}
                </div>
                <div class="product-card-body">
                    <p class="product-card-name">{safe_name}</p>
                    <p class="product-card-store">{safe_store}</p>
                </div>
            </div>
            """
        )

        price_col, save_col = st.columns([6, 1], gap="small")
        with price_col:
            st.html(f'<p class="product-card-price">{safe_price}</p>')
        with save_col:
            save_label = "♥" if saved else "♡"
            if st.button(
                save_label,
                key=f"save_{prefix}_{item['id']}_{idx}",
                help="Save to favorites",
                type="secondary",
            ):
                if save_to_favorites(item):
                    st.toast("Saved to favorites")
                else:
                    st.toast("Already in favorites")


def render_favorite_card(fv, idx, col):
    img = normalize_image_url(fv.get("imageUrl", ""))
    store = fv.get("store", "ASOS").upper()
    link = fv.get("link", "")
    safe_name = html.escape(fv.get("name", ""))
    safe_store = html.escape(store)
    safe_price = html.escape(fv.get("price", "N/A"))
    safe_img = html.escape(img)
    image_html = (
        f'<img src="{safe_img}" class="product-card-image" alt="{safe_name}">'
        if img
        else '<div class="product-card-image"></div>'
    )
    open_action_html = ""
    if link:
        open_action_html = f"""
            <a href="{html.escape(link)}" target="_blank" rel="noopener noreferrer"
               class="product-card-open" title="Open on {safe_store}"
               aria-label="Open on {safe_store}">
                {ICON_EXTERNAL}
            </a>
        """

    with col:
        st.html(
            f"""
            <div class="product-card">
                <div class="product-card-media">
                    {image_html}
                    {open_action_html}
                </div>
                <div class="product-card-body">
                    <p class="product-card-name">{safe_name}</p>
                    <p class="product-card-store">{safe_store}</p>
                </div>
            </div>
            """
        )

        price_col = st.columns([1], gap="small")[0]
        with price_col:
            st.html(f'<p class="product-card-price">{safe_price}</p>')


# =========================
# HOME PAGE
# =========================
if page == "Home":

    collection = COLLECTIONS[requested_collection()]
    home_category = ASOS_CATEGORIES[collection["category_key"]]
    home_prefs = {
        "favorite_colors": [],
        "preferences": [],
        "sleeve_length": [],
        "skirt_length": [],
        "pants_length": "both",
        "fit_style": [],
        "shoe_types": [],
        "price_min": 0,
        "price_max": 1500,
    }

    render_collection_header(
        collection["title"],
        collection["note"],
        kicker=collection["kicker"]
    )

    loading_slot = st.empty()
    render_loading_state(loading_slot, "Curating selection")
    home_products = fetch_storefront_products_cached(
        home_category["id"],
        home_category["name"],
        json.dumps(home_prefs, sort_keys=True),
        0
    )
    loading_slot.empty()

    home_products = [
        product
        for product in home_products
        if product.get("store", "ASOS").upper() in selected_stores
    ]
    home_products = sort_for_storefront(home_products)

    rendered_count = render_product_grid(
        home_products,
        prefix="home",
        columns=4,
        limit=64
    )

    if rendered_count == 0:
        st.warning("No products are available for the selected stores.")


# =========================
# SHOP PAGE
# =========================
elif page == "Shop":

    render_collection_header(
        "Search the edit",
        "Refine categories, stores, fit and color from the menu.",
        kicker="Product search"
    )

    relevant = {
        k: v
        for k, v in ASOS_CATEGORIES.items()
        if (
            u_gender == "Other"
            or v["gender"] == u_gender
        )
    }

    sel_cat = st.selectbox(
        "Category",
        [v["name"] for v in relevant.values()]
    )

    if st.button("View Products"):

        cat_id = next(
            v["id"]
            for v in relevant.values()
            if v["name"] == sel_cat
        )

        loading_slot = st.empty()
        render_loading_state(loading_slot, "Refining selection")
        products = fetch_products_cached(
            cat_id,
            sel_cat,
            json.dumps(user_prefs, sort_keys=True),
            offset=(page_num - 1) * 48
        )
        loading_slot.empty()

        products = [
            product
            for product in products
            if product.get("store", "ASOS").upper() in selected_stores
        ]

        if not products:

            st.warning(
                "No products or provider searches returned for the selected stores."
            )

            st.stop()

        st.info(f"{len(products)} products fetched.")

        matches = filter_products(
            products,
            sel_cat
        )

        if not matches:
            st.warning("We couldn't find items that match all your filters. Try removing one and search again.")
            st.stop()

        if matches:

            matches.sort(
                key=lambda x: (
                    x["data"].get("store", "ASOS").upper() in {"ASOS", "SHEIN"},
                    not x["star"]
                ),
                reverse=False
            )

            st.success(
                f"✨ {len(matches)} matches found!"
            )

            cols = st.columns(3)

            for idx, m_info in enumerate(matches):

                render_product_card(
                    m_info,
                    idx,
                    cols[idx % 3]
                )


# =========================
# SIGN IN PAGE
# =========================
elif page == "Sign In":

    render_collection_header(
        "Sign in",
        "Save your style preferences and keep your edit close.",
        kicker="Account"
    )

    st.html(
        """
        <div class="signin-panel">
            <p class="signin-copy">
                Create a lightweight local profile for this browsing session.
                Your saved items and fit notes stay on this machine.
            </p>
        </div>
        """
    )

    sign_col, _ = st.columns([1, 2])
    with sign_col:
        sign_name = st.text_input(
            "Name",
            value="" if u_name == "Guest" else u_name,
            placeholder="Enter your name",
            key="signin_name"
        )
        sign_gender = st.selectbox(
            "Preference",
            ["Female", "Male", "Other"],
            index=["Female", "Male", "Other"].index(u_gender)
            if u_gender in ["Female", "Male", "Other"]
            else 0,
            key="signin_gender"
        )
        if st.button("Continue"):
            if sign_name:
                save_profile({"name": sign_name, "gender": sign_gender})
                st.session_state.user_name = sign_name
                st.session_state.gender = sign_gender
                st.success("Signed in locally.")
            else:
                st.warning("Enter your name to continue.")


# =========================
# FAVORITES PAGE
# =========================
elif page == "Favorites":

    render_collection_header(
        "Saved items",
        "Pieces you marked for later.",
        kicker="Favorites"
    )

    favs = load_favorites()

    if not favs:

        st.info("No favorites yet.")

    else:

        if st.button("Clear Favorites"):

            with open(FAVORITES_FILE, "w") as f:
                json.dump([], f)

            st.rerun()

        cols = st.columns(3)

        for idx, fv in enumerate(favs):
            render_favorite_card(fv, idx, cols[idx % 3])
