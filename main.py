# =========================
# main.py (PRODUCTION VERSION)
# =========================

import json
import os
import requests
import urllib3
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


API_KEY = st.secrets["RAPIDAPI_KEY"]

ASOS_HOST = st.secrets.get("ASOS_HOST", "asos2.p.rapidapi.com")
SHEIN_HOST = st.secrets.get("SHEIN_HOST", "shein-data-api.p.rapidapi.com")
HM_HOST = st.secrets.get("HM_HOST", "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com")

PROFILE_FILE = "user_profile.json"
# =========================
# ASOS CATEGORIES
# =========================
ASOS_CATEGORIES = {
    "1": {"name": "Dresses", "id": "8799", "gender": "Female"},
    "2": {"name": "Tops/Shirts (Women)", "id": "4169", "gender": "Female"},
    "3": {"name": "Skirts", "id": "2639", "gender": "Female"},
    "4": {"name": "Women's Trousers", "id": "2640", "gender": "Female"},
    "5": {"name": "Women's Shoes", "id": "4172", "gender": "Female"},
    "6": {"name": "Men's Trousers", "id": "4208", "gender": "Male"},
    "7": {"name": "Men's Shirts", "id": "3602", "gender": "Male"},
    "8": {"name": "Men's T-shirts", "id": "7616", "gender": "Male"},
    "9": {"name": "Men's Shoes", "id": "4209", "gender": "Male"}
}

# =========================
# SESSION (performance boost)
# =========================
session = requests.Session()


# =========================
# PROFILE
# =========================
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4, ensure_ascii=False)


# =========================
# SMART QUERY 
# =========================
def build_smart_query(cat_name, user_prefs):
    clean_cat = cat_name.replace("Dresses", "dress").replace("Skirts", "skirt").replace("Shirts", "shirt").replace("Tops", "top").replace("Trousers", "pants").lower()
    
    parts = []
    
    # 1. צבע (תמיד טוב להוסיף)
    colors = user_prefs.get("favorite_colors", [])
    if colors:
        parts.append(colors[0])

    skirts = user_prefs.get("skirt_length", [])
    sleeves = user_prefs.get("sleeve_length", [])

    # 2. הפיצול שלך: חצאיות/שמלות מקבלות רק פילטר אורך תחתון
    if "dress" in clean_cat or "skirt" in clean_cat:
        if skirts:
            parts.append(skirts[0])
        parts.append(clean_cat)

    # 3. הפיצול שלך: חולצות מקבלות רק פילטר שרוולים
    elif "top" in clean_cat or "shirt" in clean_cat:
        if sleeves:
            s = sleeves[0]
            if s == "long": parts.append("long sleeve")
            elif s == "short": parts.append("short sleeve")
            elif s == "3/4": parts.append("3/4 sleeve")
        parts.append(clean_cat)
        
    # 4. כל שאר הדברים (מכנסיים, נעליים)
    else:
        parts.append(clean_cat)

    return " ".join(parts).strip()


# =========================
# SAFE REQUEST WRAPPER
# =========================
def safe_get(url, headers, params):
    try:
        res = session.get(
            url,
            headers=headers,
            params=params,
            verify=False,
            timeout=45
        )

        if res.status_code != 200:
            api_name = url.split("/")[2]
            print(f"❌ חסימה מ-{api_name}! סטטוס: {res.status_code}. חסר לך Subscribe ב-RapidAPI.")
            return None

        return res.json()

    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return None


# =========================
# PRICE NORMALIZER & CONVERTER
# =========================
def convert_to_ils(price_str):
    if not price_str or price_str == "N/A": return "N/A"
    clean_price = "".join(filter(lambda x: x.isdigit() or x == '.', str(price_str)))
    try:
        val = float(clean_price)
        if "£" in price_str: return f"₪{round(val * 4.7)}"
        if "$" in price_str: return f"₪{round(val * 3.7)}"
        if "€" in price_str: return f"₪{round(val * 4.0)}"
        return f"₪{round(val)}"
    except:
        return price_str

def normalize_price(raw):
    try:
        if isinstance(raw, dict):
            text = (
                raw.get("current", {}).get("text")
                or raw.get("text")
                or raw.get("value")
            )
            return convert_to_ils(text) if text else "N/A"
        return convert_to_ils(raw) if raw else "N/A"
    except:
        return "N/A"


# =========================
# ASOS
# =========================
def fetch_asos_products(cat_id, offset=0):
    url = f"https://{ASOS_HOST}/products/v2/list"
    data = safe_get(
        url,
        {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": ASOS_HOST,
        },
        {
            "store": "ROW",
            "offset": str(offset),
            "categoryId": cat_id,
            "limit": "48",         # הגדלנו את הכמות
            "country": "IL",
            "currency": "ILS",
            "lang": "en-GB",
            "sort": "price_asc"
        }
    )
    if not data: return []
    products = data.get("products", [])
    if not isinstance(products, list): return []

    out = []
    for p in products:
        img = p.get("imageUrl", "")
        if img.startswith("//"): img = "https:" + img
        out.append({
            "id": f"asos_{p.get('id')}",
            "name": p.get("name", "Unknown"),
            "price": {"current": {"text": normalize_price(p.get("price"))}},
            "imageUrl": img,
            "store": "ASOS"
        })
    return out


# =========================
# SHEIN
# =========================
def fetch_shein_products(query, page=1):

    data = safe_get(
        f"https://{SHEIN_HOST}/products/search",
        {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": SHEIN_HOST,
        },
        {
            "keyword": query,
            "page": str(page),
            "limit": "20",
        }
    )

    if not data:
        return []

    products = (
        data.get("products")
        or data.get("data", {}).get("products")
        or data.get("results")
    )

    if not isinstance(products, list):
        return []

    return _normalize(products, "shein")


# =========================
# H&M
# =========================
def fetch_hm_products(query, page=1):

    data = safe_get(
        f"https://{HM_HOST}/products/list",
        {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": HM_HOST,
        },
        {
            "country": "us",
            "lang": "en",
            "currentpage": str(page),
            "pagesize": "30",
            "query": query,
        }
    )

    if not data:
        return []

    products = (
        data.get("products")
        or data.get("data", {}).get("products")
        or data.get("results")
    )

    if not isinstance(products, list):
        return []

    return _normalize(products, "hm")


# =========================
# NORMALIZER (UNIFIED FORMAT)
# =========================
def _normalize(products, store):

    out = []

    for p in products:

        if not isinstance(p, dict):
            continue

        price = normalize_price(p.get("price"))

        out.append({
            "id": f"{store}_{p.get('id', 'x')}",
            "name": p.get("name") or p.get("title") or "Unknown",
            "price": {
                "current": {
                    "text": price
                }
            },
            "imageUrl": p.get("imageUrl") or p.get("image") or "",
            "store": store.upper()
        })

    return out


# =========================
# DEDUP (important for production)
# =========================
def deduplicate(products):

    seen = set()
    unique = []

    for p in products:
        key = p.get("name", "").lower()

        if key in seen:
            continue

        seen.add(key)
        unique.append(p)

    return unique


# =========================
# AGGREGATOR
# =========================
def get_all_products(cat_id, cat_name, user_prefs, offset=0):
    # בונים חיפוש חכם לשיין ו-H&M שמתחיל בשם הקטגוריה (למשל: "Dresses maxi long sleeve")
    base_query = build_smart_query(cat_name, user_prefs)
    if cat_name.lower() not in base_query.lower():
        query = f"{cat_name} {base_query}".strip()
    else:
        query = base_query

    current_page = (offset // 48) + 1

    # ASOS: חיפוש לפי ID של דף הקטגוריה (הכי מדויק)
    asos = fetch_asos_products(cat_id, offset)
    
    # SHEIN & HM: חיפוש חופשי אבל ממוקד בקטגוריה
    shein = fetch_shein_products(query, current_page)
    hm = fetch_hm_products(query, current_page)

    all_products = asos + shein + hm
    all_products = deduplicate(all_products)

    print(f"TOTAL: {len(all_products)} | ASOS: {len(asos)} | SHEIN: {len(shein)} | HM: {len(hm)}")
    return all_products


# =========================
# ENTRY
# =========================
def main():
    print("\n=== SmartCart PRODUCTION BACKEND ===")

    user = load_profile()

    if not user:
        print("No profile found.")
    else:
        print(f"Welcome back {user['name']}")

    print("Run: streamlit run app.py")


if __name__ == "__main__":
    main()