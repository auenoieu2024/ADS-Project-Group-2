"""Smart Packing List - Short Trips (< 4 days)"""

from datetime import datetime, date
import re
import unicodedata
from copy import deepcopy

# -----------------------
# Global state
# -----------------------
STATE = {}
MAX_DAYS_AHEAD = 120  # for trip date warning


# -----------------------
# 1. Welcome + Info Input
# -----------------------

def welcome():
    print("===============================================")
    print("        Welcome to Smart Packing List!")
    print("===============================================")
    print("Let’s get you ready for your next trip ✈️")
    input("Press Enter to start...")


def create_packing_list_name():
    print()
    name = input("What’s your name? ")
    print("\nHow would you define your gender?")
    print("\n1. Male \n2. Female\n3. Non-Binary\n4. Other\n5. Wish not to answer")
    gender = input("\nEnter the number that relates to you: ")
    destination = input("Where are you traveling to? ")

    list_name = f"{name.strip().title()}'s packing list for {destination.strip().title()}"

    STATE["name"] = name.strip()
    STATE["gender"] = gender.strip()
    STATE["destination"] = destination.strip()
    STATE["list_name"] = list_name

    print(f"\nGreat! We'll call this: \"{list_name}\"")


# -----------------------
# 2. Trip length & dates
# -----------------------

def ask_trip_length():
    print()
    while True:
        nights = input("How many nights/evenings will you be away? ").strip()
        days   = input("How many full days will you have there? ").strip()

        if not (nights.isdigit() and days.isdigit()):
            print("Please enter whole numbers only (for example: 3 nights, 2 days).")
            continue

        nights = int(nights)
        days = int(days)

        if nights < 0 or days < 0:
            print("Numbers can’t be negative.")
            continue

        if nights > 4 or days >= 4:
            print("\nThis program is only meant for short trips (< 4 days).")
            continue

        STATE["nights"] = nights
        STATE["full_days"] = days
        break


def _yes_no(prompt):
    while True:
        ans = input(prompt + " (y/n) ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer with y or n.")


def ask_trip_start_date():
    print()
    print("When does your trip start? Example: 25 10 14")
    while True:
        raw = input("YY MM DD: ").strip()
        parts = raw.split()
        if len(parts) != 3:
            print("Please type it like this: 25 10 14")
            continue
        try:
            yy, mm, dd = (int(p) for p in parts)
            year = 2000 + yy
            start = date(year, mm, dd)  # validates month/day
        except ValueError:
            print("Please use valid date numbers like 25 10 14.")
            continue

        today = date.today()
        days_until = (start - today).days

        if days_until < 0:
            print("That date is in the past. Please check the date and try again.")
            continue

        if days_until > MAX_DAYS_AHEAD:
            msg = f"That date is in {days_until} days — are you sure that is correct?"
            if not _yes_no(msg):
                print("No problem—let’s try again.")
                continue

        if days_until > 14:
            print("\nWeather data becomes uncertain more than a week ahead.")
            print("Because your trip is still", days_until, "days away, packing advice might not be precise.")
            if not _yes_no("Would you like to continue anyway?"):
                print("Okay—come back anytime. We’ll pick up from here.")
                return
            STATE["continue_with_far_date"] = True

        STATE["trip_start_date"] = start
        STATE["days_until_trip"] = days_until
        break


# -----------------------
# 3. Airline hash table 
# -----------------------

AIRLINES = {
    '1': {'airline': 'Aegean Airlines',
          'dimensions_cm': '56×45×25',
          'extras': None,
          'source_url': 'https://en.aegeanair.com/travel-info/travelling-with-aegean/baggage/baggage-allowance/',
          'weight_kg': '8.0'},

    '2': {'airline': 'Aer Lingus',
          'dimensions_cm': '55×40×24 (48×33×20 on Regional)',
          'extras': '(7 on Regional)',
          'source_url': 'https://www.aerlingus.com/prepare/bags/carry-on-baggage/',
          'weight_kg': '10.0'},

    '3': {'airline': 'Air Europa',
          'dimensions_cm': '55×35×25',
          'extras': None,
          'source_url': 'https://www.aireuropa.com/uk/en/aea/travel-information/baggage/carry-on-luggage.html',
          'weight_kg': '10.0'},

    '4': {'airline': 'Air France',
          'dimensions_cm': '55×35×25',
          'extras': '(Economy total with personal item)',
          'source_url': 'https://russia.airfrance.com/en/information/bagages/bagage-cabine-soute',
          'weight_kg': '12.0'},

    '5': {'airline': 'Austrian Airlines',
          'dimensions_cm': '56×36×23',
          'extras': None,
          'source_url': 'https://www.austrian.com/gb/en/carry-on-baggage',
          'weight_kg': '7.0'},

    '6': {'airline': 'British Airways',
          'dimensions_cm': '56×45×25',
          'extras': 'no limit - (must be able to lift to overhead)',
          'source_url': 'https://www.britishairways.com/content/information/baggage-essentials',
          'weight_kg': None},

    '7': {'airline': 'Brussels Airlines',
          'dimensions_cm': '55×40×23',
          'extras': None,
          'source_url': 'https://www.brusselsairlines.com/us/en/extra-services/baggage/carry-on-baggage',
          'weight_kg': '8.0'},

    '8': {'airline': 'Corendon Airlines',
          'dimensions_cm': '55×40×25',
          'extras': None,
          'source_url': 'https://www.corendonairlines.com/baggage-allowance/hand-luggage',
          'weight_kg': '10.0'},

    '9': {'airline': 'Finnair',
          'dimensions_cm': '55×40×23',
          'extras': '(Economy)',
          'source_url': 'https://www.finnair.com/en/baggage-on-finnair-flights/carry-on-baggage',
          'weight_kg': '8.0'},

    '10': {'airline': 'Iberia',
           'dimensions_cm': '56×40×25',
           'extras': None,
           'source_url': 'https://www.iberia.com/gb/faqs/hand-luggage/',
           'weight_kg': '10.0'},

    '11': {'airline': 'IcelandAir',
           'dimensions_cm': '55×40×20',
           'extras': '(Economy)',
           'source_url': 'https://www.icelandair.com/en-gb/support/baggage/',
           'weight_kg': '10.0'},

    '12': {'airline': 'Jet2',
           'dimensions_cm': '56×45×25',
           'extras': None,
           'source_url': 'https://www.jet2.com/en/faqs?category=hand-luggage-allowances&topic=baggage-and-sports-equipment',
           'weight_kg': '10.0'},

    '13': {'airline': 'KLM',
           'dimensions_cm': '55×35×25',
           'extras': '(Economy total with personal item)',
           'source_url': 'https://www.klm.com/information/baggage/hand-baggage-allowance',
           'weight_kg': '12.0'},

    '14': {'airline': 'Polish Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.lot.com/us/en/help-center/baggage/what-is-the-limit-of-the-carry-on-baggage',
           'weight_kg': '8.0'},

    '15': {'airline': 'Lufthansa',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.lufthansa.com/gb/en/carry-on-baggage',
           'weight_kg': '8.0'},

    '16': {'airline': 'Luxair',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.luxair.lu/en/information/baggage',
           'weight_kg': '8.0'},

    '17': {'airline': 'Norwegian',
           'dimensions_cm': '55×40×23',
           'extras': '(Flex; combined)',
           'weight_kg': '15.0'},

    '18': {'airline': 'Pegasus Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'weight_kg': '8.0'},

    '19': {'airline': 'RyanAir',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://www.ryanair.com/gb/en/lp/travel-extras/bag-sizers-and-gate-bag-fees-explained',
           'weight_kg': '10.0'},

    '20': {'airline': 'SWISS',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.swiss.com/gb/en/prepare/baggage/hand-baggage',
           'weight_kg': '8.0'},

    '21': {'airline': 'Scandinavian Airlines SAS',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.sas.se/hjalp-och-kontakt/fragor-och-svar/baggage/hur-mycket-kabinbagage-kan-jag-ta-med-mig/',
           'weight_kg': '8.0'},

    '22': {'airline': 'SunExpress',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.sunexpress.com/en-gb/information/luggage-info/hand-baggage/',
           'weight_kg': '8.0'},

    '23': {'airline': 'Air Portugal TAP',
           'dimensions_cm': '55×40×20',
           'extras': '(Europe; some routes 10)',
           'source_url': 'https://www.flytap.com/en-gb/information/baggage/hand-baggage',
           'weight_kg': '8.0'},

    '24': {'airline': 'TUI Airways',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://www.tui.co.uk/destinations/info/luggage-allowance',
           'weight_kg': '10.0'},

    '25': {'airline': 'Transavia',
           'dimensions_cm': '55×40×25',
           'extras': '(combined hand + cabin bag)',
           'source_url': 'https://www.transavia.com/help/en-eu/baggage/cabin-baggage/how-much-to-bring',
           'weight_kg': '10.0'},

    '26': {'airline': 'Transavia France',
           'dimensions_cm': '55×40×25',
           'extras': '(combined hand + cabin bag)',
           'source_url': 'https://www.transavia.com/help/en-eu/baggage/cabin-baggage',
           'weight_kg': '10.0'},

    '27': {'airline': 'Turkish Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.turkishairlines.com/en-int/any-questions/carry-on-baggage/',
           'weight_kg': '8.0'},

    '28': {'airline': 'Virgin Atlantic',
           'dimensions_cm': '56×36×23',
           'extras': '(Economy/Premium)',
           'source_url': 'https://www.virginatlantic.com/en-EU/help/categories/d8087189-4ce8-4491-8b61-f62b3b677a15',
           'weight_kg': '10.0'},

    '29': {'airline': 'Vueling',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://help.vueling.com/hc/en-gb/articles/19798835176081-Hand-Luggage-Allowance-Cabin-bags-allowance',
           'weight_kg': '10.0'},

    '30': {'airline': 'vueling (for Spain)',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://help.vueling.com/hc/en-gb/articles/19798835176081-Hand-Luggage-Allowance-Cabin-bags-allowance',
           'weight_kg': '10.0'},

    '31': {'airline': 'Wizz Air',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://wizzair.com/information-and-services/travel-information/baggage',
           'weight_kg': '10.0'},

    '32': {'airline': 'AirBaltic',
           'dimensions_cm': '55×40×23',
           'extras': ' (standard; options to buy more)',
           'source_url': 'https://www.airbaltic.com/en/baggage/',
           'weight_kg': '8.0'},

    '33': {'airline': 'EasyJet',
           'dimensions_cm': '56×45×25',
           'extras': None,
           'source_url': 'https://www.easyjet.com/en/help-centre/policy-terms-and-conditions/fees-charges',
           'weight_kg': '15.0'}
}


def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def _normalize_name(s: str) -> str:
    s = _strip_accents(s.lower())
    s = re.sub(r'\(.*?\)', ' ', s)              
    s = re.sub(r'\b(airlines?|airways)\b', ' ', s) 
    s = re.sub(r'[^a-z0-9]+', ' ', s)             
    return re.sub(r'\s+', ' ', s).strip()


def build_airline_index(AIRLINES: dict) -> dict:
    """name/alias -> airline record"""
    idx = {}
    for rec in AIRLINES.values():
        name = rec.get("airline", "")
        if not name:
            continue
        n = _normalize_name(name)
        if n:
            idx[n] = rec
            idx[n.replace(" ", "")] = rec   # compact variant

    aliases = {
        "ba": "British Airways",
        "klm": "KLM",
        "sas": "Scandinavian Airlines SAS",
        "lot": "Polish Airlines",
        "tap": "Air Portugal TAP",
        "virgin": "Virgin Atlantic",
        "wizz": "Wizz Air",
        "vueling spain": "vueling (for Spain)",
        "ryanair": "RyanAir",
    }
    name_to_rec = {v["airline"]: v for v in AIRLINES.values()}
    for alias, canonical in aliases.items():
        rec = name_to_rec.get(canonical)
        if rec:
            a = _normalize_name(alias)
            idx[a] = rec
            idx[a.replace(" ", "")] = rec
    return idx


def _ask_weight_kg():
    while True:
        try:
            w = float(input("Enter max carry-on weight in kg (0 if no stated limit): ").strip())
            if w < 0:
                print("Please enter a number ≥ 0.")
                continue
            if w == 0:
                return "0"
            return str(int(w)) if float(w).is_integer() else str(w)
        except ValueError:
            print("Please enter a valid number (e.g., 8 or 10).")


_dim_re = re.compile(r'^\s*(\d{2,3})\s*[x×]\s*(\d{2,3})\s*[x×]\s*(\d{2,3})\s*$')


def _ask_dimensions_cm():
    while True:
        raw = input("Enter max dimensions in cm (e.g., 55x40x23): ").lower().replace(" ", "")
        raw = raw.replace('x', '×')
        match = _dim_re.match(raw.replace('×', 'x'))
        if not match:
            print("Please use a pattern like 55x40x23 (only numbers).")
            continue
        L, W, H = match.groups()
        return f"{L}×{W}×{H}"


def ask_airline_by_name(AIRLINES, STATE):
    index = build_airline_index(AIRLINES)

    print("\nWhich airline are you travelling with?")
    user_airline = input("Type your airline name: ").strip()
    key1 = _normalize_name(user_airline)
    key2 = key1.replace(" ", "")

    rec = index.get(key1) or index.get(key2)

    if rec:
        weight = rec.get("weight_kg")
        dims   = rec.get("dimensions_cm")
        url    = rec.get("source_url")
        extras = rec.get("extras")

        print("\nCarry-on allowance (from our table):")
        if weight is None:
            print("  • Max weight: no published fixed limit (must be able to lift to overhead)")
        else:
            print(f"  • Max weight:      {weight} kg" + (f", {extras}" if extras else ""))
        if dims:
            print(f"  • Max dimensions:  {dims}")
        if url:
            print(f"  • More info:       {url}")

        STATE["airline"]   = rec.get("airline")
        STATE["weight_kg"] = "0" if weight is None else str(weight)
        STATE["dimensions_cm"] = dims
        return

    print("\nHmm, I couldn’t find that airline in the list.")
    print("Let’s capture the rules you see on your airline’s website.")
    user_w  = _ask_weight_kg()
    user_dm = _ask_dimensions_cm()

    print("\nThanks! We’ll use these:")
    if user_w == "0":
        print("  • Max weight: no fixed limit (treat carefully!)")
    else:
        print(f"  • Max weight:      {user_w} kg")
    print(f"  • Max dimensions:  {user_dm}")

    STATE["airline"]        = user_airline.strip()
    STATE["weight_kg"]      = user_w
    STATE["dimensions_cm"]  = user_dm


# -----------------------
# 4. Activities Hash Table
# -----------------------

activity_template = {
    "Sightseeing": {
        "Daypack": 1,
        "City Walking Shoes": 1,
        "Camera": 1
    },
    "Family / Friends": {
        "Gift / Small Present": 1
    },
    "Swimming / Surfing": {
        "Swimwear": 1,
        "Swim Goggles": 1,
        "Beach Towel": 1,
        "Rash Guard / Wetsuit": 1
    },
    "Outdoor / Adventure": {
        "Hiking Boots": 1,
        "Rain Jacket": 1,
        "Day Hiking Pack": 1
    },
    "Work / Study": {
        "Notebook / Laptop": 1,
        "Notebook / Study Materials": 1
    },
    "Formal Event / Party": {
        "Shirt / Blouse (Formal)": 1,
        "Dress / Suit": 1,
        "Formal Shoes": 1
    }
}

activity_weight = {
    "Daypack":               {"weather": "All", "weight": 0.50},
    "City Walking Shoes":    {"weather": "All", "weight": 0.80},
    "Camera":                {"weather": "All", "weight": 0.40},
    "Gift / Small Present":  {"weather": "All", "weight": 0.30},
    "Swim Goggles":          {"weather": "All", "weight": 0.10},
    "Beach Towel":           {"weather": "All", "weight": 0.40},
    "Rash Guard / Wetsuit":  {"weather": "All", "weight": 0.70},
    "Hiking Boots":          {"weather": "All", "weight": 1.20},
    "Rain Jacket":           {"weather": "All", "weight": 0.40},
    "Day Hiking Pack":       {"weather": "All", "weight": 0.60},
    "Notebook / Laptop":     {"weather": "All", "weight": 1.50},
    "Notebook / Study Materials": {"weather": "All", "weight": 0.80},
    "Shirt / Blouse (Formal)": {"weather": "All", "weight": 0.20},
    "Dress / Suit":          {"weather": "All", "weight": 0.80},
    "Formal Shoes":          {"weather": "All", "weight": 1.00},
}


def choose_activities():
    print("\nWhat activities will you do on this trip?")
    print("1. Sightseeing")
    print("2. Family / Friends")
    print("3. Swimming / Surfing")
    print("4. Outdoor / Adventure")
    print("5. Work / Study")
    print("6. Formal Event / Party")

    activities = [
        "Sightseeing",
        "Family / Friends",
        "Swimming / Surfing",
        "Outdoor / Adventure",
        "Work / Study",
        "Formal Event / Party"
    ]

    chosen = []
    print("\nAnswer yes/no for each activity:\n")
    for name in activities:
        ans = input(name + "? (yes/no): ").strip().lower()
        if ans.startswith("y"):
            chosen.append(name)
    return chosen


# -----------------------
# 5. Temperature + clothes
# -----------------------

def temp():
    print("\nWhat is the average expected temperature for your trip?")
    print("1. Freezing (<0°C)")
    print("2. Cold (0°C - 10°C)")
    print("3. Cool (11°C - 20°C)")
    print("4. Warm (20°C - 25°C)")
    print("5. Hot (>25°C)")

    while True:
        choice = input("Enter 1–5: ").strip()
        if choice == "1":
            return "Freezing"
        if choice == "2":
            return "Cold"
        if choice == "3":
            return "Cool"
        if choice == "4":
            return "Warm"
        if choice == "5":
            return "Hot"
        print("Please enter a number between 1 and 5.")
        
#Hash table of clothes + weight

clothes = {
    # Freezing
    "Heavy Coat":      {"weather": "Freezing", "weight": 1.0},
    "Thermal Shirt":   {"weather": "Freezing", "weight": 0.25},
    "Thermal Leggings":{"weather": "Freezing", "weight": 0.30},
    "Wool Sweater":    {"weather": "Freezing", "weight": 0.50},
    "Long-Sleeve Shirt":{"weather": "Freezing", "weight": 0.20},
    "Jeans":           {"weather": "Freezing", "weight": 0.60},
    "Winter Pants":    {"weather": "Freezing", "weight": 0.70},
    "Scarf":           {"weather": "Freezing", "weight": 0.20},
    "Beanie":          {"weather": "Freezing", "weight": 0.10},
    "Gloves":          {"weather": "Freezing", "weight": 0.15},
    "Thick Socks":     {"weather": "Freezing", "weight": 0.10},
    "Undershirt":      {"weather": "Freezing", "weight": 0.15},
    "Boots":           {"weather": "Freezing", "weight": 1.20},

    # Cold
    "Coat":            {"weather": "Cold", "weight": 0.80},
    "Sweater":         {"weather": "Cold", "weight": 0.45},
    "Cardigan":        {"weather": "Cold", "weight": 0.40},
    "Long-Sleeve Shirt (Cold)": {"weather": "Cold", "weight": 0.20},
    "Turtleneck":      {"weather": "Cold", "weight": 0.30},
    "Jeans (Cold)":    {"weather": "Cold", "weight": 0.60},
    "Warm Pants":      {"weather": "Cold", "weight": 0.70},
    "Warm Socks":      {"weather": "Cold", "weight": 0.10},
    "Closed Shoes":    {"weather": "Cold", "weight": 0.90},
    "Scarf (Cold)":    {"weather": "Cold", "weight": 0.20},
    "Beanie (Cold)":   {"weather": "Cold", "weight": 0.10},

    # Cool
    "Light Jacket":    {"weather": "Cool", "weight": 0.40},
    "Sweatshirt":      {"weather": "Cool", "weight": 0.35},
    "Hoodie":          {"weather": "Cool", "weight": 0.45},
    "T-shirt":         {"weather": "Cool", "weight": 0.15},
    "Long-Sleeve Shirt (Cool)": {"weather": "Cool", "weight": 0.20},
    "Jeans (Cool)":    {"weather": "Cool", "weight": 0.60},
    "Chinos":          {"weather": "Cool", "weight": 0.50},
    "Sneakers":        {"weather": "Cool", "weight": 0.70},
    "Socks":           {"weather": "Cool", "weight": 0.05},

    # Warm
    "Short-Sleeve Top": {"weather": "Warm", "weight": 0.12},
    "T-shirt (Warm)":   {"weather": "Warm", "weight": 0.15},
    "Light Pants":      {"weather": "Warm", "weight": 0.35},
    "Shorts":           {"weather": "Warm", "weight": 0.20},
    "Casual Dress":     {"weather": "Warm", "weight": 0.25},
    "Sneakers (Warm)":  {"weather": "Warm", "weight": 0.70},
    "Socks (Warm)":     {"weather": "Warm", "weight": 0.05},
    "Light Jacket (Evening)": {"weather": "Warm", "weight": 0.35},
    "Sun Hat (Warm)":   {"weather": "Warm", "weight": 0.10},

    # Hot
    "Tank Top":         {"weather": "Hot", "weight": 0.10},
    "T-shirt (Hot)":    {"weather": "Hot", "weight": 0.15},
    "Shorts (Hot)":     {"weather": "Hot", "weight": 0.20},
    "Summer Dress":     {"weather": "Hot", "weight": 0.25},
    "Light Shirt":      {"weather": "Hot", "weight": 0.18},
    "Swimwear":         {"weather": "Hot", "weight": 0.15},
    "Flip-Flops":       {"weather": "Hot", "weight": 0.20},
    "Sun Hat":          {"weather": "Hot", "weight": 0.10},
    "Light Sandals":    {"weather": "Hot", "weight": 0.30},
    "Beach Cover-Up":   {"weather": "Hot", "weight": 0.20},

    # All
    "Toiletries": {"weather": "All", "weight": 0.80},
}

template = {
    "Freezing": {
        "Heavy Coat": 1, "Thermal Shirt": 2, "Thermal Leggings": 2,
        "Wool Sweater": 1, "Long-Sleeve Shirt": 2, "Jeans": 1,
        "Winter Pants": 1, "Scarf": 1, "Beanie": 1, "Gloves": 1,
        "Thick Socks": 3, "Undershirt": 2, "Boots": 1, "Toiletries": 1},

    "Cold": {
        "Coat": 1, "Sweater": 1, "Cardigan": 1,
        "Long-Sleeve Shirt (Cold)": 2, "Turtleneck": 1,
        "Jeans (Cold)": 1, "Warm Pants": 1, "Warm Socks": 3,
        "Closed Shoes": 1, "Scarf (Cold)": 1, "Beanie (Cold)": 1,
        "Toiletries": 1},

    "Cool": {
        "Light Jacket": 1, "Sweatshirt": 1, "Hoodie": 1,
        "T-shirt": 2, "Long-Sleeve Shirt (Cool)": 1,
        "Jeans (Cool)": 1, "Chinos": 1, "Sneakers": 1,
        "Socks": 3, "Toiletries": 1},

    "Warm": {
        "Short-Sleeve Top": 2, "T-shirt (Warm)": 2,
        "Light Pants": 1, "Shorts": 1, "Casual Dress": 1,
        "Sneakers (Warm)": 1, "Socks (Warm)": 3,
        "Light Jacket (Evening)": 1, "Sun Hat (Warm)": 1,
        "Toiletries": 1},

    "Hot": {
        "Tank Top": 2, "T-shirt (Hot)": 2, "Shorts (Hot)": 2,
        "Summer Dress": 1, "Light Shirt": 1, "Swimwear": 1,
        "Flip-Flops": 1, "Sun Hat": 1, "Light Sandals": 1,
        "Beach Cover-Up": 1, "Toiletries": 1}
}


def show_items(quantities):
    print("\nPacking list:\n")
    total = 0.0
    for item, qty in quantities.items():
        print(item + ":", qty)

        if item in clothes:
            weight = clothes[item]["weight"]
        elif item in activity_weight:
            weight = activity_weight[item]["weight"]
        else:
            weight = 0.0

        total += weight * qty

    print("\nTotal weight:", round(total, 2), "kg")
    return total


def edit_items(quantities):
    print("\nEdit the quantities(press Enter to keep current):\n")

    for item in list(quantities.keys()):
        current = quantities[item]
        print(item, "(current:", current, ")")
        new_val = input("New quantity: ")

        if new_val == "":
            continue
        if new_val.isdigit():
            quantities[item] = int(new_val)
            if quantities[item] == 0:
                del quantities[item]
        else:
            print("Not a number. Keeping previous value.")
    return quantities


# Merge clothes + activity_weight into one weight table for trimming
WEIGHT_TABLE = {}
WEIGHT_TABLE.update(clothes)
WEIGHT_TABLE.update(activity_weight)

# -----------------------
# 6. Greedy Algorithm
# ----------------------

def total_weight(quantities, weight_table):
    w = 0.0
    for item, qty in quantities.items():
        if item in weight_table:
            w += weight_table[item]["weight"] * qty
    return round(w, 3)


PRIORITY_RANK = {"Underwear": 0, "Socks": 1, "T-shirt": 2, "Jeans": 2,
                 "Sneakers": 4, "Toiletries": 5}


def _priority(item):
    return PRIORITY_RANK.get(item, 5)


HARD_KEEP = {"Underwear", "Socks"}


def show_weight_status(items, weight_table, limit_kg, buffer=0.3):
    tw = total_weight(items, weight_table)
    target = float(limit_kg) - float(buffer)
    print(f"\n[Weight] total={tw} kg  |  limit={limit_kg} kg  |  target ≤ {round(target, 2)} kg")
    margin = round(target - tw, 3)
    if margin >= 0.8:
        print("Status: ✅ OK (comfortable margin)")
    elif margin >= 0:
        print("Status: ⚠️ Close to the limit")
    else:
        print("Status: ❌ Over the limit")


def greedy_trim_to_limit_verbose(items, weight_table, limit_kg,
                                 safety_buffer=0.3, respect_hard_keep=True, max_passes=2):
    target = max(0.0, float(limit_kg) - float(safety_buffer))
    current = deepcopy(items)
    before = total_weight(current, weight_table)
    removed_trace = []
    if before <= target:
        return current, {"before": before, "after": before, "note": "Already within target."}

    def sorted_units(avoid_hard):
        units = [(i, 1) for i, q in current.items() for _ in range(q)]
        def key(u):
            item = u[0]
            pri = _priority(item)
            if avoid_hard and item in HARD_KEEP:
                pri = -100
            w = weight_table.get(item, {}).get("weight", 0.0)
            return (pri, w)
        units.sort(key=key, reverse=True)
        return units

    for pass_id in range(max_passes):
        avoid_hard = respect_hard_keep and pass_id == 0
        units = sorted_units(avoid_hard)
        for item, _ in units:
            if total_weight(current, weight_table) <= target:
                break
            if avoid_hard and item in HARD_KEEP:
                continue
            if current.get(item, 0) > 0:
                current[item] -= 1
                if current[item] == 0:
                    del current[item]
                removed_trace.append(item)
        if total_weight(current, weight_table) <= target:
            break

    after = total_weight(current, weight_table)
    note = "Reached target." if after <= target else "Could not reach target without cutting essentials."
    info = {"before": before, "after": after, "removed": removed_trace, "note": note}
    return current, info


def run_trim_final(items, use_verbose=True, safety_buffer=0.3):
    limit = float(STATE.get("weight_kg") or 10.0)
    print("\n--- Before Trim ---")
    show_weight_status(items, WEIGHT_TABLE, limit, buffer=safety_buffer)
    trimmed, info = greedy_trim_to_limit_verbose(items, WEIGHT_TABLE, limit,
                                                 safety_buffer=safety_buffer,
                                                 respect_hard_keep=True, max_passes=2)
    print("\n--- After Trim ---")
    show_weight_status(trimmed, WEIGHT_TABLE, limit, buffer=safety_buffer)
    if info.get("removed"):
        print("Removed:", ", ".join(info["removed"]))
    print(info.get("note", ""))
    return trimmed, info


# -----------------------
# 7. Main 
# -----------------------

def main():
    # Intro + basic info
    welcome()
    create_packing_list_name()
    ask_trip_length()
    ask_trip_start_date()

    # Airline (sets STATE["weight_kg"], STATE["dimensions_cm"])
    ask_airline_by_name(AIRLINES, STATE)

    # Activities
    activities = choose_activities()
    STATE["activities"] = activities

    # Temperature → base packing template
    weather = temp()
    items = template[weather].copy()

    # Add activity-specific items
    for act in activities:
        extra_items = activity_template.get(act, {})
        for item, qty in extra_items.items():
            items[item] = items.get(item, 0) + qty

    # Show packing list + total weight
    total_kg = show_items(items)

    # Let user edit (clothes + activity items)
    if input("\nDo you want change the number of your clothes? (yes/no): ").lower().startswith("y"):
        edit_items(items)
        total_kg = show_items(items)

    # Check against airline weight limit (if we have one)
    limit_str = STATE.get("weight_kg")
    if limit_str and limit_str != "0":
        try:
            limit = float(limit_str)
            if total_kg > limit:
                print(f"\nYour list is over your airline's carry-on limit of {limit} kg.")
                if input("Do you want help reducing the list automatically? (yes/no): ").lower().startswith("y"):
                    trimmed, info = run_trim_final(items)
                    items.clear()
                    items.update(trimmed)
                    total_kg = show_items(items)
        except ValueError:
            pass

    print("\nThanks! Your packing list is ready ✅")

    print("\nInfo collected so far (for debugging):")
    for k, v in STATE.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

