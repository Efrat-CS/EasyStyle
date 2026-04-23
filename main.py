import json
import os

PROFILE_FILE = "user_profile.json"

def create_user_profile():
    print("--- Welcome to SmartCart Fashion Setup ---")
    
    # פונקציית עזר 1: מוודאת שלא השאירו שדה ריק
    def get_input(prompt):
        while True:
            val = input(prompt).strip()
            if val: 
                return val
            print("❌ This field cannot be empty. Please try again.")

    # פונקציית עזר 2: מוודאת שהקלט קיים ברשימה המותרת
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
            break
        except ValueError:
            print("❌ Invalid input! Please enter a valid number (e.g., 165).")
    
    valid_tops = ['xs', 's', 'm', 'l', 'xl']
    while True:
        top_size = get_input("Your top size (XS, S, M, L, XL): ").lower()
        if top_size in valid_tops:
            top_size = top_size.upper()
            break
        print(f"❌ Invalid size! Please choose from: {', '.join(valid_tops).upper()}")
    
    while True:
        bottom_input = get_input("Your bottom size (e.g., 38, 40): ")
        try:
            bottom_size = int(bottom_input)
            if 32 <= bottom_size <= 50:
                break
            print("❌ Please enter a realistic bottom size (32-50).")
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")
    
    while True:
        shoe_input = get_input("Your shoe size (e.g., 38, 39): ")
        try:
            shoe_size = int(shoe_input)
            if 34 <= shoe_size <= 46:
                break
            print("❌ Please enter a realistic shoe size (34-46).")
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")
    
    # --- אימות הרשימות הסגורות המורחבות ---
    sleeve_length = get_valid_list_input(
        "Preferred sleeve lengths (sleeveless, short, elbow, 3/4, long, extra_long - comma separated): ", 
        ['sleeveless', 'short', 'elbow', '3/4', 'long', 'extra_long']
    )
    
    skirt_length = get_valid_list_input(
        "Preferred skirt lengths (micro, mini, knee, midi, tea, maxi, floor - comma separated): ", 
        ['micro', 'mini', 'knee', 'midi', 'tea', 'maxi', 'floor']
    )
    
    fit_style = get_valid_list_input(
        "Preferred fits (skinny, slim, regular, relaxed, oversized, loose, flare, straight - comma separated): ", 
        ['skinny', 'slim', 'regular', 'relaxed', 'oversized', 'loose', 'flare', 'straight']
    )
    
    # --- רשימות פתוחות (טקסט חופשי) ---
    colors_input = get_input("Enter favorite colors (comma separated, e.g., black, blue): ")
    favorite_colors = [c.strip() for c in colors_input.split(',')]
    
    style_input = get_input("Enter style preferences (comma separated, e.g., modest, leather): ")
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
    print(f"\n[System]: Profile saved successfully to {PROFILE_FILE}!")

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

def main():
    user_data = load_profile()
    
    if user_data:
        print(f"\n--- Welcome back, {user_data['name']}! ---")
        print("Your fashion DNA is ready:")
        print(f"- Skirt lengths: {', '.join(user_data['skirt_length'])}")
        print(f"- Sleeve lengths: {', '.join(user_data['sleeve_length'])}")
        print(f"- Fits: {', '.join(user_data['fit_style'])}")
        print(f"- Colors: {', '.join(user_data['favorite_colors'])}")
        print(f"- Styles: {', '.join(user_data['preferences'])}")
    else:
        user_data = create_user_profile()
        save_profile(user_data)
    
    print("\n[System]: Analyzing Zara's catalog for matching items...")

if __name__ == "__main__":
    main()