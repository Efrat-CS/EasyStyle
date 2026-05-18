# =========================
# app.py
# =========================

import streamlit as st
import os
import json
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

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

    raw_id = str(product["id"]).split("_")[-1]

    store = product.get("store", "ASOS").upper()

    if store == "HM":

        link = (
            "https://www2.hm.com/en_us/"
            f"search-results.html?q={product['name'].replace(' ', '+')}"
        )

    elif store == "SHEIN":

        link = (
            "https://www.shein.com/"
            f"search?keyword={product['name'].replace(' ', '%20')}"
        )

    else:

        link = f"https://www.asos.com/prd/{raw_id}"

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


# =========================
# Streamlit setup
# =========================
st.set_page_config(
    page_title="EasyStyle AI",
    page_icon="👗",
    layout="wide"
)

st.title("👗 EasyStyle: Your Visual AI Stylist")


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
        st.session_state.user_name
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
def render_product_card(m_info, idx, col):
    item = m_info["data"]
    store = item.get("store", "ASOS").upper()

    with col:
        img = item.get("imageUrl", "")
        if img.startswith("//"):
            img = "https:" + img
        elif img and not img.startswith("http"):
            img = "https://" + img

        if img:
            st.image(img, use_container_width=True)

        star = "⭐ " if m_info["star"] else ""
        st.markdown(f"**{star}{item['name']}**")
        st.caption(f"📍 {store}")

        price_text = (
            item.get("price", {})
            .get("current", {})
            .get("text", "N/A")
        )
        st.write(f"💰 {price_text}")

        raw_id = str(item["id"]).split("_")[-1]

        if store == "HM":
            link = f"https://www2.hm.com/en_us/search-results.html?q={item['name'].replace(' ', '+')}"
        elif store == "SHEIN":
            link = f"https://www.shein.com/search?keyword={item['name'].replace(' ', '%20')}"
        else:
            link = f"https://www.asos.com/prd/{raw_id}"

        st.link_button(f"🛍️ Buy on {store}", link)

        if st.button("❤️ Save", key=f"save_{item['id']}_{idx}"):
            if save_to_favorites(item):
                st.toast("Saved!")
            else:
                st.toast("Already saved!")

        st.divider()


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

            with cols[idx % 3]:

                if fv.get("imageUrl"):

                    st.image(
                        fv["imageUrl"],
                        use_container_width=True
                    )

                st.markdown(f"**{fv['name']}**")

                st.caption(f"📍 {fv.get('store', '')}")

                st.write(f"💰 {fv['price']}")

                st.link_button(
                    "🛍️ View Product",
                    fv["link"]
                )

                st.divider()