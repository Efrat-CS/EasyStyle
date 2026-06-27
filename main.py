# =========================
# main.py (PRODUCTION VERSION)
# =========================

import json
import os
import requests
import urllib3
import streamlit as st
from urllib.parse import quote_plus

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


API_KEY = st.secrets["RAPIDAPI_KEY"]

ASOS_HOST = st.secrets.get("ASOS_HOST", "asos2.p.rapidapi.com")
SHEIN_HOST = st.secrets.get("SHEIN_HOST", "shein-data-api.p.rapidapi.com")
HM_HOST = st.secrets.get("HM_HOST", "apidojo-hm-hennes-mauritz-v1.p.rapidapi.com")

PROFILE_FILE = "user_profile.json"

# Providers without a configured product API are still useful as direct store
# searches. They let the user compare the same style across many shops.
SEARCH_PROVIDERS = [
    {
        "store": "ZARA",
        "display_name": "Zara",
        "url": "https://www.zara.com/il/en/search?searchTerm={query}",
    },
    {
        "store": "HM",
        "display_name": "H&M",
        "url": "https://www2.hm.com/en_us/search-results.html?q={query}",
    },
    {
        "store": "CASTRO",
        "display_name": "Castro",
        "url": "https://www.castro.com/catalogsearch/result/?q={query}",
    },
    {
        "store": "RENUAR",
        "display_name": "Renuar",
        "url": "https://www.renuar.co.il/catalogsearch/result/?q={query}",
    },
    {
        "store": "MANGO",
        "display_name": "Mango",
        "url": "https://shop.mango.com/il/en/search?kw={query}",
    },
    {
        "store": "TERMINAL X",
        "display_name": "Terminal X",
        "url": "https://www.terminalx.com/catalogsearch/result/?q={query}",
    },
    {
        "store": "TWENTYFOURSEVEN",
        "display_name": "TwentyFourSeven",
        "url": "https://www.twentyfourseven.co.il/catalogsearch/result/?q={query}",
    },
    {
        "store": "GOLF",
        "display_name": "Golf",
        "url": "https://www.golf-il.co.il/catalogsearch/result/?q={query}",
    },
    {
        "store": "FOX",
        "display_name": "Fox",
        "url": "https://www.fox.co.il/catalogsearch/result/?q={query}",
    },
    {
        "store": "PULL&BEAR",
        "display_name": "Pull&Bear",
        "url": "https://www.pullandbear.com/il/search?searchTerm={query}",
    },
    {
        "store": "BERSHKA",
        "display_name": "Bershka",
        "url": "https://www.bershka.com/il/search?searchTerm={query}",
    },
    {
        "store": "STRADIVARIUS",
        "display_name": "Stradivarius",
        "url": "https://www.stradivarius.com/il/search?searchTerm={query}",
    },
    {
        "store": "NEXT",
        "display_name": "Next",
        "url": "https://www.next.co.il/en/search?w={query}",
    },
    {
        "store": "GAP",
        "display_name": "GAP",
        "url": "https://www.gap.com/browse/search.do?searchText={query}",
    },
    {
        "store": "UNIQLO",
        "display_name": "Uniqlo",
        "url": "https://www.uniqlo.com/eu/en/search?q={query}",
    },
    {
        "store": "URBAN OUTFITTERS",
        "display_name": "Urban Outfitters",
        "url": "https://www.urbanoutfitters.com/search?q={query}",
    },
    {
        "store": "NIKE",
        "display_name": "Nike",
        "url": "https://www.nike.com/il/w?q={query}",
    },
    {
        "store": "ADIDAS",
        "display_name": "Adidas",
        "url": "https://www.adidas.com/us/search?q={query}",
    },
]

STORE_OPTIONS = list(dict.fromkeys(
    ["ASOS", "SHEIN"] + [provider["store"] for provider in SEARCH_PROVIDERS]
))

STORE_DISPLAY = {
    provider["store"]: provider["display_name"]
    for provider in SEARCH_PROVIDERS
}

STORE_SEARCH_URLS = {
    provider["store"]: provider["url"]
    for provider in SEARCH_PROVIDERS
}

CATEGORY_IMAGE_URLS = {
    "dress": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=800&q=80",
    "skirt": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80",
    "top": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=800&q=80",
    "shirt": "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=800&q=80",
    "pants": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80",
    "trousers": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=800&q=80",
    "shoes": "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
}

ZARA_CATEGORY_URLS = {
    "Dresses": "https://www.zara.com/il/en/woman-dresses-l1066.html?ajax=true",
    "Tops/Shirts (Women)": "https://www.zara.com/il/en/woman-tops-l1322.html?ajax=true",
    "Skirts": "https://www.zara.com/il/en/woman-skirts-l1299.html?ajax=true",
    "Women's Trousers": "https://www.zara.com/il/en/woman-trousers-l1335.html?ajax=true",
    "Women's Shoes": "https://www.zara.com/il/en/woman-shoes-l1251.html?ajax=true",
    "Men's Trousers": "https://www.zara.com/il/en/man-trousers-l838.html?ajax=true",
    "Men's Shirts": "https://www.zara.com/il/en/man-shirts-l737.html?ajax=true",
    "Men's T-shirts": "https://www.zara.com/il/en/man-tshirts-l855.html?ajax=true",
    "Men's Shoes": "https://www.zara.com/il/en/man-shoes-l769.html?ajax=true",
}

# H&M blocks backend requests from this local environment, but the same products
# are visible in the browser. Keep a small real fallback instead of blank cards.
HM_REAL_DRESS_PRODUCTS = [
    {
        "name": "OPEN-SHOULDER DRESS WITH TIE BELT",
        "price": "$49.99",
        "url": "https://www2.hm.com/en_us/productpage.1348280001.html",
        "imageUrl": "https://image.hm.com/assets/hm/ac/87/ac879a3dda9e079a2d088c1178d24cbaa79c9365.jpg?imwidth=657",
    },
    {
        "name": "LONG T-SHIRT DRESS",
        "price": "$24.99",
        "url": "https://www2.hm.com/en_us/productpage.1331397007.html",
        "imageUrl": "https://image.hm.com/assets/hm/d7/8b/d78b5b562de9c5dbdb3ae19dd5a4bf0af6c7bc37.jpg?imwidth=657",
    },
    {
        "name": "RUFFLE-TRIMMED COTTON DRESS",
        "price": "$4.99",
        "url": "https://www2.hm.com/en_us/productpage.1123540016.html",
        "imageUrl": "https://image.hm.com/assets/hm/65/bb/65bbb0c1647d2f21a8b334095279ceb082c38024.jpg?imwidth=657",
    },
    {
        "name": "DRESS WITH TULLE SKIRT",
        "price": "$5.99",
        "url": "https://www2.hm.com/en_us/productpage.1281499016.html",
        "imageUrl": "https://image.hm.com/assets/hm/4c/74/4c746321decdd29f256667bcc0a71065b0d40f98.jpg?imwidth=657",
    },
    {
        "name": "SLEEVELESS SEERSUCKER DRESS",
        "price": "$4.99",
        "url": "https://www2.hm.com/en_us/productpage.1317437008.html",
        "imageUrl": "https://image.hm.com/assets/hm/02/cb/02cb08597e75477fa7fa781f74b9b36c4112e46d.jpg?imwidth=657",
    },
    {
        "name": "COTTON MUSLIN DRESS",
        "price": "$5.99",
        "url": "https://www2.hm.com/en_us/productpage.1199571014.html",
        "imageUrl": "https://image.hm.com/assets/hm/43/77/43772b312605cd827a1844c002dbc250a6ad8eb5.jpg?imwidth=657",
    },
    {
        "name": "PRINTED COTTON DRESS",
        "price": "$3.99",
        "url": "https://www2.hm.com/en_us/productpage.1308684005.html",
        "imageUrl": "https://image.hm.com/assets/hm/d4/71/d471f20c708d55cee792d635f4f4449ae0a412ec.jpg?imwidth=657",
    },
]


def category_image_url(cat_name):
    name = cat_name.lower()
    for key, image_url in CATEGORY_IMAGE_URLS.items():
        if key in name:
            return image_url
    return CATEGORY_IMAGE_URLS["default"]


def build_store_item_name(store, query, cat_name):
    display_name = STORE_DISPLAY.get(store, store.title())
    item_query = query or cat_name
    duplicate_phrases = {
        "Dresses dress": "dress",
        "Skirts skirt": "skirt",
        "Tops/Shirts (Women) top/shirts (women)": "top",
        "Women's Trousers women's pants": "pants",
        "Women's Shoes women's shoes": "shoes",
        "Men's Trousers men's pants": "pants",
        "Men's Shirts men's shirt": "shirt",
        "Men's T-shirts men's t-shirts": "t-shirt",
        "Men's Shoes men's shoes": "shoes",
    }
    item_query = duplicate_phrases.get(item_query, item_query)
    return f"{display_name} {item_query}".strip()
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
            timeout=15
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
# REAL STORE PRODUCTS
# =========================
def _zara_image(product):
    colors = product.get("detail", {}).get("colors", [])
    for color in colors:
        for media in color.get("xmedia", []):
            if media.get("type") != "image":
                continue
            delivery_url = media.get("extraInfo", {}).get("deliveryUrl")
            if delivery_url:
                return delivery_url
            image_url = media.get("url", "")
            if image_url:
                return image_url.replace("{width}", "850")
    return ""


def _zara_product_url(product):
    seo = product.get("seo", {})
    keyword = seo.get("keyword")
    seo_product_id = seo.get("seoProductId")
    product_id = product.get("id")
    if keyword and seo_product_id:
        return (
            "https://www.zara.com/il/en/"
            f"{keyword}-p{seo_product_id}.html?v1={product_id}"
        )
    return STORE_SEARCH_URLS["ZARA"].format(query=quote_plus(product.get("name", "")))


def fetch_zara_products(cat_name, limit=12):
    url = ZARA_CATEGORY_URLS.get(cat_name)
    if not url:
        return []

    try:
        res = session.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/126 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
            },
            timeout=20,
        )
        if res.status_code != 200:
            print(f"ZARA fetch failed: {res.status_code}")
            return []
        data = res.json()
    except Exception as e:
        print(f"ZARA fetch error: {e}")
        return []

    products = []
    for group in data.get("productGroups", []):
        for element in group.get("elements", []):
            for product in element.get("commercialComponents", []):
                if product.get("type") != "Product":
                    continue

                image_url = _zara_image(product)
                if not image_url:
                    continue

                price = product.get("price")
                products.append({
                    "id": f"zara_{product.get('id')}",
                    "name": product.get("name", "Zara product"),
                    "price": {"current": {"text": f"₪{round(price / 100)}" if price else "N/A"}},
                    "imageUrl": image_url,
                    "store": "ZARA",
                    "url": _zara_product_url(product),
                    "providerSearch": False,
                })
                if len(products) >= limit:
                    return products

    return products


def fetch_hm_real_fallback(cat_name, limit=8):
    if "Dresses" not in cat_name:
        return []

    products = []
    for idx, product in enumerate(HM_REAL_DRESS_PRODUCTS[:limit]):
        products.append({
            "id": f"hm_real_{idx}_{product['url'].split('.')[-2]}",
            "name": product["name"],
            "price": {"current": {"text": normalize_price(product["price"])}},
            "imageUrl": product["imageUrl"],
            "store": "HM",
            "url": product["url"],
            "providerSearch": False,
        })
    return products


def build_provider_search_cards(query, cat_name, user_prefs):
    return fetch_zara_products(cat_name) + fetch_hm_real_fallback(cat_name)


def build_store_fallback_cards(query, cat_name, stores):
    encoded_query = quote_plus(query)
    image_url = category_image_url(cat_name)

    cards = []
    for store in stores:
        url_template = STORE_SEARCH_URLS.get(store)
        if not url_template:
            continue

        cards.append({
            "id": f"fallback_{store.lower().replace(' ', '_').replace('&', 'and')}_{encoded_query}",
            "name": build_store_item_name(store, query, cat_name),
            "price": {"current": {"text": "Store search"}},
            "imageUrl": image_url,
            "store": store,
            "url": url_template.format(query=encoded_query),
            "providerSearch": True,
        })

    return cards


# =========================
# DEDUP (important for production)
# =========================
def deduplicate(products):

    seen = set()
    unique = []

    for p in products:
        key = p.get("id") if p.get("providerSearch") else p.get("name", "").lower()

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
    provider_cards = build_provider_search_cards(query, cat_name, user_prefs)

    fallback_cards = []

    all_products = asos + shein + hm + provider_cards + fallback_cards
    all_products = deduplicate(all_products)

    print(
        f"TOTAL: {len(all_products)} | ASOS: {len(asos)} | "
        f"SHEIN: {len(shein)} | HM: {len(hm)} | "
        f"PROVIDER SEARCHES: {len(provider_cards)} | "
        f"FALLBACKS: {len(fallback_cards)}"
    )
    return all_products


def get_storefront_products(cat_id, cat_name, user_prefs, offset=0):
    base_query = build_smart_query(cat_name, user_prefs)
    if cat_name.lower() not in base_query.lower():
        query = f"{cat_name} {base_query}".strip()
    else:
        query = base_query

    asos = fetch_asos_products(cat_id, offset)
    provider_cards = build_provider_search_cards(query, cat_name, user_prefs)

    all_products = deduplicate(asos + provider_cards)
    print(
        f"STOREFRONT TOTAL: {len(all_products)} | ASOS: {len(asos)} | "
        f"REAL STORE PRODUCTS: {len(provider_cards)}"
    )
    return all_products


# =========================
# ENTRY
# =========================
def main():
    print("\n=== Célune PRODUCTION BACKEND ===")

    user = load_profile()

    if not user:
        print("Sorry. No profile found.")
    else:
        print(f"Welcome back {user['name']}")

    print("Run: uv run streamlit run app.py to start the application.")


if __name__ == "__main__":
    main()
