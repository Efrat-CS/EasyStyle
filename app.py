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
    get_all_products,
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
        .product-card {
            background: #ffffff;
            border: 1px solid #ececec;
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            overflow: hidden;
            margin-bottom: 0;
        }
        .product-card-media {
            position: relative;
            background: #f7f7f7;
        }
        .product-card-image {
            width: 100%;
            aspect-ratio: 3 / 4;
            object-fit: cover;
            display: block;
        }
        .product-card-open {
            position: absolute;
            top: 12px;
            right: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 1px solid rgba(20, 20, 20, 0.08);
            background: rgba(255, 255, 255, 0.94);
            color: #111111;
            text-decoration: none;
            opacity: 0;
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(0, 0, 0, 0.10);
            backdrop-filter: blur(10px);
            pointer-events: none;
            transition: opacity 0.16s ease, transform 0.16s ease, border-color 0.15s ease, background 0.15s ease;
        }
        .product-card-media:hover .product-card-open,
        .product-card-open:focus-visible {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }
        .product-card-open:hover {
            border-color: rgba(20, 20, 20, 0.24);
            background: #ffffff;
            color: #111111;
        }
        .product-card-open::before {
            content: "\\2197";
            font-size: 1rem;
            font-weight: 600;
            line-height: 1;
        }
        .product-card-open svg {
            display: none;
        }
        .product-card-star {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 4px 10px;
            font-size: 0.72rem;
            font-weight: 600;
            color: #1a1a1a;
            letter-spacing: 0.02em;
        }
        .product-card-body {
            padding: 14px 14px 13px;
        }
        .product-card-name {
            margin: 0;
            font-size: 0.88rem;
            font-weight: 500;
            line-height: 1.45;
            color: #1a1a1a;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.55rem;
        }
        .product-card-store {
            margin: 6px 0 0;
            font-size: 0.68rem;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #9a9a9a;
        }
        .product-card-price {
            margin: 0;
            padding-top: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #111111;
            letter-spacing: 0;
        }
        div[data-testid="stVerticalBlock"] > div:has(.product-card) {
            gap: 0.4rem;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) button {
            width: 42px !important;
            min-width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            border: 1px solid #e4e4e4 !important;
            background: #ffffff !important;
            color: #222222 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1.14rem !important;
            line-height: 1 !important;
            box-shadow: none !important;
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
            border-color: #111111 !important;
            background: #fafafa !important;
            color: #c45c6a !important;
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) {
            align-items: center;
            padding: 12px 14px 14px;
            border: 1px solid #ececec;
            border-top: 1px solid #f2f2f2;
            border-radius: 0 0 12px 12px;
            margin-top: -1px;
            margin-bottom: 1.25rem;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        div[data-testid="column"] div[data-testid="stHorizontalBlock"]:has(.product-card-price) > div {
            display: flex;
            align-items: center;
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
    page_title="SmartCart AI",
    page_icon="👗",
    layout="wide"
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
st.title("👗 SmartCart: Your Visual AI Stylist")


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

    st.header("📍 Navigation")

    page = st.radio(
        "Go to:",
        ["Shop", "My Favorites ❤️"]
    )

    st.divider()

    st.header("⚙️ Your Profile")

    u_name = st.text_input(
        "Name",
        value="",
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
    st.subheader("📄 Pages (More Items!)")
    page_num = st.number_input("Page Number", min_value=1, value=1, step=1)

    st.subheader("🧠 Filter Mode")

    filter_mode = st.radio(
        "Logic",
        [
            "Smart (High Recall)",
            "Strict (Exact Name Match)"
        ]
    )

    st.subheader("💰 Price Range")

    min_p, max_p = st.slider(
        "ILS",
        0,
        1500,
        (50, 600)
    )

    st.subheader("📏 Lengths & Fit")

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

    st.subheader("👟 Shoes")

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

    st.subheader("🎨 Style Bonuses")

    colors_t = st.text_input(
        "Favorite Colors"
    )

    style_t = st.text_input(
        "Style Keywords"
    )


# =========================
# Guard
# =========================
if not u_name or u_gender == "Select...":

    st.info(
        "👋 Please enter your name and gender to continue."
    )

    st.stop()


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
# SHOP PAGE
# =========================
if page == "Shop":

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

    if st.button("🔍 Find My Style"):

        cat_id = next(
            v["id"]
            for v in relevant.values()
            if v["name"] == sel_cat
        )

        with st.spinner(f"Fetching products from Page {page_num}..."):

            products = get_all_products(
                cat_id,
                sel_cat,
                user_prefs,
                offset=(page_num - 1) * 48
            )

        if not products:

            st.warning(
                "No products returned from APIs."
            )

            st.stop()

        st.info(
            f"📦 {len(products)} products fetched."
        )

        matches = filter_products(
            products,
            sel_cat
        )

        if not matches:
            st.warning("We couldn't find items that match all your filters. Try removing one and search again! 👗")
            st.stop()

        if matches:

            matches.sort(
                key=lambda x: x["star"],
                reverse=True
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
# FAVORITES PAGE
# =========================
elif page == "My Favorites ❤️":

    st.header("💖 Your Saved Items")

    favs = load_favorites()

    if not favs:

        st.info("No favorites yet.")

    else:

        if st.button("🗑️ Clear Favorites"):

            with open(FAVORITES_FILE, "w") as f:
                json.dump([], f)

            st.rerun()

        cols = st.columns(3)

        for idx, fv in enumerate(favs):
            render_favorite_card(fv, idx, cols[idx % 3])
