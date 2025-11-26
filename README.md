# ADS-Project-Group-2

# Table of contents
1. Introduction
2. Feature
3. Files
4. Prerequisites & Environment
5. Installation & Execution
6. Usage Guide
7. Data Structures & Algorithms
8. Streamlit Front-End
9. Further Improvements
10. Bibliography & Webgraphy
11. Credits

# Introduction of Our Product: Personalized Packing List & Weight Estimator
As a traveler, you enter basic trip details (destination, duration, temperature range, activities, and airline). The app generates a categorized packing list you can customiz and estimates luggage weight, including your carry-on base weight, then compares it to your selected airline’s limit. 
If you’re near or over the limit, it offers Smart Suggestions to swap or reduce items.

# Feature
- Trip intake: Destination, days, temperature band (Freezing/Cold/Cool/Warm/Hot), activities (e.g., Sightseeing, Swimming/Surfing, Outdoor & Adventure, Work & Study, Formal Event/Party Family & Friends), and airline selection or manual baggage rules
  
- Auto-generated packing list: Categorized into Clothing, Toiletries, Gadgets & Accessories, Shoes, Documents & Essentials, tuned to your inputs using predefined templates.
  
- Customize: Check/uncheck, change quantities, add new items with weight category (Light < 0.3 kg, Medium 0.3–0.8 kg, Heavy > 0.8 kg).
  
- Weight Estimator: Adds up the carry-on’s base weight + all items (from a built-in weight library and user additions) and shows total estimated weight.

- Airline Weight Indicator: Shows a color signal based on the weight status — Green (under limit), Yellow (close to limit), and Red (over limit).

- Smart Suggestions: If near/over limit, proposes swaps and reductions (e.g., “Swap boots (1.2 kg) for sneakers (0.7 kg)”, “You may not need a heavy jacket at 25 °C”, “Mix & match 4 tops with 2 bottoms for 7 days”).


# File
`Final_code_project.py` — Main program: trip intake → packing list generator → weight estimator → airline check → smart suggestions → save/load.

Contains:
- Input screens/prompts
- Category builders for Clothing / Toiletries / Gadgets & Accessories / Shoes / Documents
- Weight library (e.g., Heavy Coat 1.0 kg, Denim Pants 0.6 kg, Shirt 0.15 kg, Scarf 0.2 kg, Shoes 0.8 kg, Toiletries 1.0 kg)
- Add-item flow (with Light/Medium/Heavy buckets)
- Greedy weight advisor (see sections 7 & 8)
- Airline limit check + color indicator

`README.md` — This document.

# Prerequisites & Environment
- Python 3.8 or later
- Our project is designed to run entirely with built-in libraries (no external installation required).

# Installation & Execution
Click Code → Download ZIP on the repository page.
Unzip to any folder.
Double-click `Final_code_project.py` to start.

# Usage Guide
1. Create Trip
Tap “+” → fill:
Trip name (e.g., “Madrid Trip”)
Duration (integer days)
Temperature band (Freezing / 0–10 Cold / 11–20 Cool / 20–25 Warm / >25 Hot)
Activities (choose one or multiple)
Airline (for baggage limit check)
Base carry-on weight (e.g., 1.0–1.5 kg)

2. Review Summary
Example:
Destination: Madrid
Duration: 7 days
Weather: Cool (11–20 °C)
Activity: Family & Friends
Airline saved for later comparison

3. Generate Packing List
App builds essentials by category; you check/uncheck and set quantities (e.g., Shirts = 3).

4. Add Items (optional)
“Add New Item” → name + weight bucket: Light / Medium / Heavy.

5. Weight Estimator
Sums: item weights × quantities + base carry-on.
Shows total and color indicator vs airline (Green <9.5 kg, Yellow ~10 kg, Red >10 kg).

6. Smart Suggestions
If near/over limit, shows concrete swap/reduce tips. Accept / decline / ignore, then recalculate.

7. Finish
Save the updated list; optionally view airline upgrade/pre-purchase info (mock).


# Data Structures & Algorithms
The following variable names are the main dictionaries used to store data of user information, airline rules, clothing items/weights, activity items/weights, templates, and all packing-related details

**Main Dictionaries**

1. STATE - holds user data: name, destination, weather, airline details, limits, activities, etc.
2. AIRLINES - database for airline baggage rules
3. activity_template - defines which items should be added when the user selects a specific activity
4. activity_weight - weights for all activity-related items
5. clothes - look up table for all clothing items with weather type and weight
6. template - default data for initial suggestion of clothes for each weather type (Freezing, Cold, Cool, Warm, Hot) with default quantity
7. items - the user’s actual packing list being built and modified
8. WEIGHT_TABLE - merged weight lookup table combining clothing weights and activity item weights
The following variable names are the supporting dictionaries used to store data of airline shortcuts, lookup indexes, item-priority rules, and trimming results

**Supporting Dictionaries**

1. aliases - common acronyms for airlines
2. index - normalised airline-name for look up
3. PRIORITY_RANK - priority levels for items used for trimming
4. info - summary dictionary after trimming
   
**Main Algorithm**

The project uses a greedy algorithm to reduce a set of items so that their total weight stays under the airline's weight limit. It  removes the item that seems best to remove at that moment. 
The algorithm starts with every item split into individual units. Instead of removing a clothing category, it removes things one at a time. Each unit is assigned a priority value, and the algorithm removes the heavier one first.
The algorithm removes items from the top of that sorted list until the weight becomes low enough, and it stops. The algorithm will not remove essential items like underwear and socks stored in HARD_KEEP to ensure important items are removed when necessary.

1. total_weight(quantities, weight_table) - Calculates the total weight of all items.
2. PRIORITY_RANK - priority levels for items used for trimming
3. _priority(item) - Looks up the rank
4. show_weight_status(items, weight_table, limit_kg, buffer=0.3) - Displays the current weight state compared to the target limit.
5. greedy_trim_to_limit_verbose - Trims items until the weight is below the weight limit

# Streamlit Front-End
This file implements the Smart Packing List – Short Trips web app using Streamlit. **https://public-c6fjnoltdjcxtqlzvegd2r.streamlit.app/**

**Sidebar:**

The sidebar is where the user enters all trip information. This includes their name, destination, travel dates, airline, baggage rules, expected weather, and activities. When the user clicks “Generate / Reset packing list,” the sidebar inputs are used to build the initial packing list. The app generates an initial packing list with the templates and shared WEIGHT_TABLE

**Main Area:**

The main area displays the results. It shows a trip summary, which also has a downloadable CSV of the list, the generated packing list, item weights, and editing options. It also shows the total weight and includes the button “Auto-trim to fit airline limit”, calls the described greedy algorithm (greedy_trim_to_limit_verbose) to automatically trim items if the list is too heavy. It updates the packing list and shows which items were removed.

# Further Improvements
- Export in other platforms for shareable packing list
- Invite collaborators
- Weather forecast integration for exact prediction per dates and destination
- Calendar import

# Bibliography & Webgraphy
ADS course slides (Simple Search, Greedy, Graphs, Trees, etc.)
Airline public baggage pages (for reference limits)

# Credits
Authors for this project are:
Loraine Nieto
Aoi Ueno
Estelle Arnandar
Eliza Whifield
Mohamed Embaby
Manvi Gupta
Seif Omara
Faris Selimovic

