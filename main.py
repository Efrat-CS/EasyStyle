import json
import os
import requests
import urllib3
from dotenv import load_dotenv

# ביטול הודעות אזהרה על חיבור
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")
PROFILE_FILE = "user_profile.json"

# --- מילון הקטגוריות של ASOS ---
ASOS_CATEGORIES = {
    "1": {"name": "Dresses", "id": "8799"},
    "2": {"name": "Tops/Shirts", "id": "4169"},
    "3": {"name": "Skirts", "id": "2639"},
    "4": {"name": "Shoes", "id": "4172"}
}

def create_user_profile():
    print("--- Welcome to EasyStyle: ASOS Edition ---")
    
    def get_input(prompt):
        while True:
            val = input(prompt).strip()
            if val: 
                return val
            print("❌ This field cannot be empty. Please try again.")

    def get_valid_list_input(prompt, valid_options):
        while True:
            val = get_input(prompt).lower()
            items = [i.strip() for i in val.split(',')]
            if all(item in valid_options for item in items):
                return items
            else:
                print(f"❌ Please choose ONLY from: {', '.join(valid_options)}")

    name = get_input("Enter your name: ")
    
    valid_genders = ['male', 'female', 'other']
    while True:
        gender = get_input("Gender (Male/Female/Other): ").lower()
        if gender in valid_genders:
            break
        print("❌ Please enter Male, Female, or Other.")
    
    while True:
        height_input = get_input("Enter your height in cm: ")
        try:
            height = int(height_input)
            if 50 <= height <= 250:
                break
            print("❌ Please enter a realistic height (50-250 cm).")
        except ValueError:
            print("❌ Invalid input! Please enter a valid number.")
    
    valid_tops = ['xs', 's', 'm', 'l', 'xl']
    while True:
        top_size = get_input("Your top size (XS, S, M, L, XL): ").lower()
        if top_size in valid_tops:
            top_size = top_size.upper()
            break
        print(f"❌ Invalid size! Please choose from: {', '.join(valid_tops).upper()}")
    
    while True:
        bottom_input = get_input("Your bottom size (e.g., 32-50): ")
        try:
            bottom_size = int(bottom_input)
            if 32 <= bottom_size <= 50:
                break
            print("❌ Please enter a realistic bottom size (32-50).")
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")

    while True:
        shoe_input = get_input("Your shoe size (e.g., 34-46): ")
        try:
            shoe_size = int(shoe_input)
            if 34 <= shoe_size <= 46:
                break
            print("❌ Please enter a realistic shoe size (34-46).")
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")
    
    sleeve_length = get_valid_list_input(
        "Preferred sleeve lengths (sleeveless, short, elbow, 3/4, long, extra_long): ", 
        ['sleeveless', 'short', 'elbow', '3/4', 'long', 'extra_long']
    )
    
    skirt_length = get_valid_list_input(
        "Preferred skirt lengths (micro, mini, knee, midi, tea, maxi, floor): ", 
        ['micro', 'mini', 'knee', 'midi', 'tea', 'maxi', 'floor']
    )
    
    fit_style = get_valid_list_input(
        "Preferred fits (skinny, slim, regular, relaxed, oversized, loose, flare, straight): ", 
        ['skinny', 'slim', 'regular', 'relaxed', 'oversized', 'loose', 'flare', 'straight']
    )
    
    colors_input = get_input("Enter favorite colors (comma separated): ")
    favorite_colors = [c.strip() for c in colors_input.split(',')]
    
    style_input = get_input("Enter style preferences (e.g., modest, leather): ")
    preferences = [s.strip() for s in style_input.split(',')]

    profile = {
        "name": name,
        "gender": gender.capitalize(),
        "height_cm": height, 
        "top_size": top_size,
        "bottom_size": bottom_size,
        "shoe_size": shoe_size,
        "sleeve_length": sleeve_length,
        "skirt_length": skirt_length,
        "fit_style": fit_style,
        "favorite_colors": favorite_colors,
        "preferences": preferences
    }
    return profile

def save_profile(profile):
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=4)
    print(f"\n[System]: Profile saved successfully!")

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

def fetch_asos_products(user_prefs, category_data):
    cat_name = category_data["name"]
    cat_id = category_data["id"]
    
    print(f"\n[System]: Analyzing ASOS {cat_name} for {user_prefs['name']}...")
    url = "https://asos2.p.rapidapi.com/products/v2/list"
    
    synonyms = {
        "maxi": ["maxi", "long", "floor length", "full length"],
        "midi": ["midi", "midaxi", "tea dress", "mid"],
        "long": ["long sleeve", "longline", "sleeved"],
        "3/4": ["3/4", "three quarter", "elbow length"]
    }

    # הגדרות ROW לשקלים, דילוג 200, מהזול ליקר - כמו שעבד לך מושלם!
    querystring = {
        "store": "ROW",      
        "offset": "200",      
        "categoryId": cat_id, 
        "limit": "48", 
        "country": "IL",     
        "sort": "priceasc",   
        "currency": "ILS",   
        "sizeSchema": "UK",  
        "lang": "en-GB"      
    }

    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "asos2.p.rapidapi.com"}

    try:
        response = requests.get(url, headers=headers, params=querystring, verify=False, timeout=20)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", []) if isinstance(data, dict) else data
            
            print(f"--- Scanning {len(products)} {cat_name}. Filtering for your Style DNA... ---\n")
            found_count = 0
            
            for item in products:
                if not isinstance(item, dict): continue
                name = item.get('name', '').lower()
                
                # --- בדיקות התאמה ---
                match_skirt = False
                for length in user_prefs['skirt_length']:
                    check_list = synonyms.get(length, [length])
                    if any(word in name for word in check_list):
                        match_skirt = True
                
                match_sleeve = False
                for sleeve in user_prefs['sleeve_length']:
                    check_list = synonyms.get(sleeve, [sleeve])
                    if any(word in name for word in check_list):
                        match_sleeve = True

                is_short = "mini" in name or "short" in name
                if any(l in ["mini", "micro"] for l in user_prefs['skirt_length']):
                    is_short = False

                is_match = False
                
                # --- לוגיקה מותאמת קטגוריה ---
                if cat_name == "Dresses":
                    if (match_skirt or match_sleeve) and not is_short: 
                        is_match = True
                elif cat_name == "Tops/Shirts":
                    if match_sleeve and not is_short: 
                        is_match = True
                elif cat_name == "Skirts":
                    if match_skirt and not is_short: 
                        is_match = True
                elif cat_name == "Shoes":
                    is_match = True # אין צנזורה על נעליים

                if is_match:
                    found_count += 1
                    price = item.get('price', {}).get('current', {}).get('text', 'N/A')
                    product_id = item.get('id') 
                    star = "⭐ " if any(c.lower() in name for c in user_prefs['favorite_colors']) else "   "
                    
                    print(f"{star}👗 {item.get('name')}")
                    print(f"   💰 Price: {price}")
                    print(f"   🔗 Link: https://www.asos.com/prd/{product_id}\n")
            
            if found_count == 0:
                print(f"😔 No matches in this batch of {cat_name}.")
            else:
                print(f"✅ Found {found_count} matches!")
        else:
            print(f"⚠️ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    user_data = load_profile()
    if not user_data:
        user_data = create_user_profile()
        save_profile(user_data)
    
    print(f"\n--- Welcome back, {user_data['name']}! ---")
    
    print("\nWhat are we shopping for today?")
    for key, value in ASOS_CATEGORIES.items():
        print(f"[{key}] {value['name']}")
        
    choice = input("\nEnter category number (1-4): ").strip()
    
    if choice in ASOS_CATEGORIES:
        fetch_asos_products(user_data, ASOS_CATEGORIES[choice])
    else:
        print("❌ Invalid choice. Please run the script again.")
    
    print("\n[System]: Analysis complete.")

if __name__ == "__main__":
    main()