import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime

# Page configuration with official brand name
st.set_page_config(
    page_title="Collabé | Creator & Café Match Network",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .brand-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(120deg, #E63946, #FB8500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .match-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
    }
    .slot-taken-card {
        background-color: #fdf2f2;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #e02424;
        margin-bottom: 15px;
    }
    .no-match-card {
        background-color: #fff8eb;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #e3a008;
        margin-bottom: 15px;
    }
    .badge-success {
        background-color: #def7ec;
        color: #03543f;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-danger {
        background-color: #fde8e8;
        color: #9b1c1c;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .admin-badge {
        background-color: #e0e7ff;
        color: #3730a3;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .hour-chip {
        display: inline-block;
        background: #eef2ff;
        color: #3730a3;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .hour-chip-free {
        display: inline-block;
        background: #ecfdf5;
        color: #065f46;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .hour-chip-busy {
        display: inline-block;
        background: #fef2f2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px;
        font-size: 0.8rem;
        font-weight: 600;
        text-decoration: line-through;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- DEAD-HOUR WINDOW DEFINITIONS & ATOMIC HOURLY BLOCKS -----------------
WINDOW_OPTIONS = [
    "Morning Window: 08:00 AM to 12:00 PM",
    "Early Afternoon: 12:00 PM to 03:00 PM",
    "Afternoon Window: 03:00 PM to 06:00 PM",
    "Post-Lunch Afternoon: 01:00 PM to 05:00 PM",
    "Evening Window: 05:00 PM to 08:00 PM",
    "Early Morning: 07:00 AM to 09:00 AM",
    "Late Evening: 08:00 PM to 10:00 PM"
]

# Atomic 1-hour slots inside standard windows
WINDOW_SUB_SLOTS = {
    "Morning Window: 08:00 AM to 12:00 PM": [
        "08:00 AM - 09:00 AM",
        "09:00 AM - 10:00 AM",
        "10:00 AM - 11:00 AM",
        "11:00 AM - 12:00 PM"
    ],
    "Early Afternoon: 12:00 PM to 03:00 PM": [
        "12:00 PM - 01:00 PM",
        "01:00 PM - 02:00 PM",
        "02:00 PM - 03:00 PM"
    ],
    "Afternoon Window: 03:00 PM to 06:00 PM": [
        "03:00 PM - 04:00 PM",
        "04:00 PM - 05:00 PM",
        "05:00 PM - 06:00 PM"
    ],
    "Post-Lunch Afternoon: 01:00 PM to 05:00 PM": [
        "01:00 PM - 02:00 PM",
        "02:00 PM - 03:00 PM",
        "03:00 PM - 04:00 PM",
        "04:00 PM - 05:00 PM"
    ],
    "Evening Window: 05:00 PM to 08:00 PM": [
        "05:00 PM - 06:00 PM",
        "06:00 PM - 07:00 PM",
        "07:00 PM - 08:00 PM"
    ],
    "Early Morning: 07:00 AM to 09:00 AM": [
        "07:00 AM - 08:00 AM",
        "08:00 AM - 09:00 AM"
    ],
    "Late Evening: 08:00 PM to 10:00 PM": [
        "08:00 PM - 09:00 PM",
        "09:00 PM - 10:00 PM"
    ]
}

def get_atomic_hours_for_selection(window, duration, slot_choice):
    """Returns the list of 1-hour atomic blocks covered by a creator's selection."""
    if window not in WINDOW_SUB_SLOTS:
        return [slot_choice] if slot_choice else [window]
    
    sub_slots = WINDOW_SUB_SLOTS[window]
    
    if duration == "Full Window" or "Full Window" in slot_choice:
        return list(sub_slots)
    elif duration == "1 Hour":
        if "Flexible" in slot_choice:
            return [sub_slots[0]]
        for s in sub_slots:
            if s in slot_choice:
                return [s]
        return [sub_slots[0]]
    elif duration == "2 Hours":
        if "Flexible" in slot_choice:
            return sub_slots[:2]
        # Match span e.g. 12:00 PM - 02:00 PM or 03:00 PM - 05:00 PM
        for i in range(len(sub_slots) - 1):
            start_p = sub_slots[i].split(" - ")[0]
            end_p = sub_slots[i+1].split(" - ")[1]
            if start_p in slot_choice and end_p in slot_choice:
                return [sub_slots[i], sub_slots[i+1]]
        return sub_slots[:2]
    elif duration == "3 Hours":
        if len(sub_slots) >= 3:
            for i in range(len(sub_slots) - 2):
                start_p = sub_slots[i].split(" - ")[0]
                end_p = sub_slots[i+2].split(" - ")[1]
                if start_p in slot_choice and end_p in slot_choice:
                    return [sub_slots[i], sub_slots[i+1], sub_slots[i+2]]
            return sub_slots[:3]
        return list(sub_slots)
    
    return [slot_choice]

# ----------------- DATA PERSISTENCE LAYER -----------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CAFES_FILE = os.path.join(DATA_DIR, "cafes.json")
CREATORS_FILE = os.path.join(DATA_DIR, "creators.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")

# Pre-seeded Chandigarh Cafés with flexible windows (Morning & Afternoon)
INITIAL_CAFES = [
    {
        "id": "cafe_1",
        "name": "The Willow Café",
        "sector": "Sector 9",
        "slots": [
            "Morning Window: 08:00 AM to 12:00 PM",
            "Early Afternoon: 12:00 PM to 03:00 PM",
            "Afternoon Window: 03:00 PM to 06:00 PM"
        ],
        "max_crew": 4,
        "allows_tripod": True,
        "has_natural_light": True,
        "allowed_shoots": ["Food & Beverage", "Fashion & Lifestyle", "UGC / Brand Content"],
        "deal_type": "Free in exchange for 1 tagged Reel",
        "manager_phone": "917814259209"
    },
    {
        "id": "cafe_2",
        "name": "Blue Tokai Coffee Roasters",
        "sector": "Sector 8",
        "slots": [
            "Morning Window: 08:00 AM to 12:00 PM",
            "Early Afternoon: 12:00 PM to 03:00 PM",
            "Afternoon Window: 03:00 PM to 06:00 PM",
            "Late Evening: 08:00 PM to 10:00 PM"
        ],
        "max_crew": 3,
        "allows_tripod": True,
        "has_natural_light": True,
        "allowed_shoots": ["Food & Beverage", "UGC / Brand Content", "Product Shoot"],
        "deal_type": "Minimum spend ₹500",
        "manager_phone": "917814259209"
    },
    {
        "id": "cafe_3",
        "name": "Backpacker's Café",
        "sector": "Sector 9",
        "slots": [
            "Morning Window: 08:00 AM to 12:00 PM",
            "Early Afternoon: 12:00 PM to 03:00 PM"
        ],
        "max_crew": 2,
        "allows_tripod": False,
        "has_natural_light": False,
        "allowed_shoots": ["Food & Beverage", "Lifestyle"],
        "deal_type": "Free coffee & meal with tag",
        "manager_phone": "917814259209"
    },
    {
        "id": "cafe_4",
        "name": "Sector 7 Social",
        "sector": "Sector 7",
        "slots": [
            "Morning Window: 08:00 AM to 12:00 PM",
            "Early Afternoon: 12:00 PM to 03:00 PM",
            "Afternoon Window: 03:00 PM to 06:00 PM"
        ],
        "max_crew": 6,
        "allows_tripod": True,
        "has_natural_light": True,
        "allowed_shoots": ["Fashion & Lifestyle", "Music / Commercial", "Product Shoot"],
        "deal_type": "Hourly fee ₹800/hr",
        "manager_phone": "917814259209"
    }
]

# Starter creators with Morning & Afternoon hourly bookings
INITIAL_CREATORS = [
    {
        "id": "creator_1",
        "name": "RajKaran",
        "handle": "@rajkaran_shoots",
        "followers": "22K",
        "whatsapp": "917814259209",
        "shoot_type": "Fashion & Lifestyle",
        "description": "Shooting seasonal lookbook reels with clothing brand",
        "preferred_sector": "Sector 9",
        "preferred_window": "Morning Window: 08:00 AM to 12:00 PM",
        "duration": "1 Hour",
        "preferred_slot": "08:00 AM - 09:00 AM (1 Hr)",
        "slot_hours": ["08:00 AM - 09:00 AM"],
        "crew_size": 3,
        "needs_tripod": True,
        "needs_natural_light": True,
        "budget_pref": "Free in exchange for 1 tagged Reel",
        "status": "Pending",
        "timestamp": "2026-10-16 10:30"
    },
    {
        "id": "creator_2",
        "name": "Raman",
        "handle": "@raman_visuals",
        "followers": "35K",
        "whatsapp": "917814259209",
        "shoot_type": "Fashion & Lifestyle",
        "description": "Footwear brand promo with 1 model",
        "preferred_sector": "Sector 9",
        "preferred_window": "Morning Window: 08:00 AM to 12:00 PM",
        "duration": "2 Hours",
        "preferred_slot": "09:00 AM - 11:00 AM (2 Hrs)",
        "slot_hours": ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM"],
        "crew_size": 3,
        "needs_tripod": True,
        "needs_natural_light": True,
        "budget_pref": "Free in exchange for 1 tagged Reel",
        "status": "Pending",
        "timestamp": "2026-10-16 10:35"
    },
    {
        "id": "creator_3",
        "name": "Deepak",
        "handle": "@deepak_creates",
        "followers": "45K",
        "whatsapp": "917814259209",
        "shoot_type": "Food & Beverage",
        "description": "Specialty coffee review and café aesthetic reel",
        "preferred_sector": "Sector 9",
        "preferred_window": "Early Afternoon: 12:00 PM to 03:00 PM",
        "duration": "1 Hour",
        "preferred_slot": "01:00 PM - 02:00 PM (1 Hr)",
        "slot_hours": ["01:00 PM - 02:00 PM"],
        "crew_size": 2,
        "needs_tripod": True,
        "needs_natural_light": True,
        "budget_pref": "Free in exchange for 1 tagged Reel",
        "status": "Pending",
        "timestamp": "2026-10-16 11:15"
    },
    {
        "id": "creator_4",
        "name": "Harman",
        "handle": "@harman_style",
        "followers": "30K",
        "whatsapp": "917814259209",
        "shoot_type": "Fashion & Lifestyle",
        "description": "Sunset golden hour fashion reel shoot",
        "preferred_sector": "Sector 9",
        "preferred_window": "Afternoon Window: 03:00 PM to 06:00 PM",
        "duration": "2 Hours",
        "preferred_slot": "03:00 PM - 05:00 PM (2 Hrs)",
        "slot_hours": ["03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"],
        "crew_size": 3,
        "needs_tripod": True,
        "needs_natural_light": True,
        "budget_pref": "Free in exchange for 1 tagged Reel",
        "status": "Pending",
        "timestamp": "2026-10-16 12:00"
    }
]

def load_data(file_path, default_data):
    if not os.path.exists(file_path):
        save_data(file_path, default_data)
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Keep session synced with disk
st.session_state.cafes = load_data(CAFES_FILE, INITIAL_CAFES)
st.session_state.creators = load_data(CREATORS_FILE, INITIAL_CREATORS)
st.session_state.bookings = load_data(BOOKINGS_FILE, [])

# ----------------- BOOKED HOURLY SLOTS TRACKING -----------------
def get_all_hours_for_cafe(cafe):
    """Returns set of all 1-hour atomic slots hosted by this cafe across its windows."""
    hours = set()
    for w in cafe.get("slots", []):
        if w in WINDOW_SUB_SLOTS:
            hours.update(WINDOW_SUB_SLOTS[w])
        else:
            hours.add(w)
    return hours

def get_booked_hours_by_cafe():
    """Returns a dict mapping cafe_id -> set of booked atomic 1-hour slots."""
    booked_map = {}
    for b in st.session_state.bookings:
        cid = b.get("cafe_id")
        if not cid:
            continue
        if cid not in booked_map:
            booked_map[cid] = set()
        
        hours = b.get("hours", [])
        if hours:
            for h in hours:
                booked_map[cid].add(h)
        else:
            slot_str = b.get("slot", "")
            win = b.get("window", "")
            dur = b.get("duration", "1 Hour")
            inferred = get_atomic_hours_for_selection(win, dur, slot_str)
            for h in inferred:
                booked_map[cid].add(h)
    return booked_map

def format_whatsapp_number(phone_str):
    """Automatically formats any 10-digit Indian number with 91 country code."""
    if not phone_str:
        return ""
    digits = "".join(filter(str.isdigit, str(phone_str)))
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return "91" + digits
    elif len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits

def get_open_hours_for_window(cafe, window):
    """Returns list of open 1-hour sub-slots for a specific window at a cafe."""
    cafe_hours = get_all_hours_for_cafe(cafe)
    all_sub = WINDOW_SUB_SLOTS.get(window, [])
    if not all_sub:
        all_sub = [window]
    booked_map = get_booked_hours_by_cafe()
    booked_for_cafe = booked_map.get(cafe["id"], set())
    return [h for h in all_sub if (h in cafe_hours or not WINDOW_SUB_SLOTS.get(window)) and h not in booked_for_cafe]

# ----------------- MATCHING ENGINE (WINDOW + HOURLY SLOTS) -----------------
def evaluate_match_with_slots(creator, cafe):
    failed_reasons = []
    
    # 1. Hard Rule: Crew Size
    if creator["crew_size"] > cafe["max_crew"]:
        failed_reasons.append(f"Crew size ({creator['crew_size']}) exceeds café limit ({cafe['max_crew']})")
    
    # 2. Hard Rule: Tripod / Lights
    if creator["needs_tripod"] and not cafe["allows_tripod"]:
        failed_reasons.append("Creator needs tripod, but café does not allow tripods")
        
    # 3. Hard Rule: Natural Light
    if creator["needs_natural_light"] and not cafe["has_natural_light"]:
        failed_reasons.append("Creator requires natural window light, which café lacks")
        
    # 4. Hourly / Window Compatibility Check
    creator_win = creator.get("preferred_window", creator.get("preferred_slot", ""))
    creator_hours = creator.get("slot_hours", [])
    if not creator_hours:
        creator_hours = get_atomic_hours_for_selection(
            creator_win, 
            creator.get("duration", "1 Hour"), 
            creator.get("preferred_slot", "")
        )
        
    cafe_hours = get_all_hours_for_cafe(cafe)
    
    # Check if cafe hosts all requested hours
    hours_offered = all(h in cafe_hours for h in creator_hours)
    if not hours_offered:
        # String match fallback
        window_match = any(creator_win in cs or cs in creator_win for cs in cafe["slots"])
        if not window_match:
            failed_reasons.append(f"Café does not host shoots during requested time ({creator.get('preferred_slot', creator_win)})")
        
    # 5. Atomic Hourly Slot Conflict Check
    booked_map = get_booked_hours_by_cafe()
    cafe_booked = booked_map.get(cafe["id"], set())
    
    conflicting_hours = [h for h in creator_hours if h in cafe_booked]
    open_sub_slots = get_open_hours_for_window(cafe, creator_win)
    
    if failed_reasons:
        return "INCOMPATIBLE", 0, failed_reasons, open_sub_slots
    
    if conflicting_hours:
        return "SLOT_TAKEN", 0, [f"Hour(s) {', '.join(conflicting_hours)} already booked by another creator!"], open_sub_slots
        
    # Scoring
    score = 75
    pref_sec = creator.get("preferred_sector", "")
    if "Any" in pref_sec or pref_sec == cafe["sector"]:
        score += 15
    creator_deal = creator.get("budget_pref", "")
    cafe_deal = cafe.get("deal_type", "")
    if "Any" in creator_deal or "Any" in cafe_deal or creator_deal == cafe_deal:
        score += 10
    elif "Discussion" in creator_deal and "Discussion" in cafe_deal:
        score += 10
        
    return "AVAILABLE", score, [], open_sub_slots

def generate_whatsapp_message(creator, cafe, slot, duration="1 Hour"):
    msg = (
        f"Hi {creator['name']}! 🎬 (via Collabé)\n\n"
        f"We found a verified shoot match in Chandigarh for your brief:\n\n"
        f"📍 Venue: {cafe['name']} ({cafe['sector']})\n"
        f"🕒 Confirmed Slot: {slot} ({duration})\n"
        f"👥 Max Crew: {cafe['max_crew']} people\n"
        f"💡 Deal Model: {cafe['deal_type']}\n"
        f"📷 Tripod: {'Allowed' if cafe['allows_tripod'] else 'No'} | Light: {'Natural' if cafe['has_natural_light'] else 'Normal'}\n\n"
        f"⚠️ Note: Slots on Collabé are locked on a first-come, first-served basis. Reply YES to accept!"
    )
    encoded = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/{creator['whatsapp']}?text={encoded}"
    return msg, wa_url

# ----------------- SIDEBAR & ACCESS CONTROL (ADMIN PIN VIA SECRETS) -----------------
st.sidebar.markdown("## 🎬 **Collabé**")
st.sidebar.markdown("*The Creator & Café Match Network*")

# Admin Authentication
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.sidebar.markdown("---")

# Dynamic Menu based on Admin Status
if st.session_state.is_admin:
    st.sidebar.markdown('<span class="admin-badge">🔓 Admin Desk Active</span>', unsafe_allow_html=True)
    nav_options = [
        "⚡ Live Matching & Real-Time Booking (Admin)",
        "📊 Live Tabular Data & Slot Status (Admin)",
        "📝 Creator / Brand Request Form (Public)", 
        "☕ Café & Venue Setup (Public)"
    ]
    if st.sidebar.button("🔒 Logout Admin"):
        st.session_state.is_admin = False
        st.rerun()
else:
    # PUBLIC VIEW: Only Registration Forms (Data & Matching are LOCKED)
    nav_options = [
        "📝 Creator / Brand Request Form", 
        "☕ Café & Venue Setup",
        "🔍 Check My Booking Status"
    ]
    st.sidebar.markdown("**🔒 Collabé Team Login:**")
    pin_input = st.sidebar.text_input("Enter Admin PIN to unlock desk:", type="password", placeholder="PIN")
    if st.sidebar.button("Unlock Admin Desk"):
        admin_secret = st.secrets.get("ADMIN_PIN", os.environ.get("ADMIN_PIN", ""))
        if admin_secret and pin_input == admin_secret:
            st.session_state.is_admin = True
            st.sidebar.success("Welcome back, Lakhwinder!")
            st.rerun()
        else:
            st.sidebar.error("Incorrect Admin PIN.")

page = st.sidebar.radio("Navigation:", nav_options)

# ----------------- PAGE: CREATOR PUBLIC FORM -----------------
if page in ["📝 Creator / Brand Request Form", "📝 Creator / Brand Request Form (Public)"]:
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Creator & Small Brand Shoot Brief Registration</div>', unsafe_allow_html=True)
    
    st.info("💡 **Flexible Morning & Afternoon Booking**: Choose only the hours you need (1 Hour, 2 Hours, or full window). Unused dead hours remain open for other creators so nothing is wasted!")
    
    # Selection of Window & Duration outside form or inside for reactive slots
    col_w1, col_w2 = st.columns(2)
    selected_window = col_w1.selectbox(
        "1. Preferred Shoot Window (Morning / Afternoon / Evening) *",
        WINDOW_OPTIONS + ["Custom Window / Other"]
    )
    selected_duration = col_w2.selectbox(
        "2. Duration Needed *",
        ["1 Hour", "2 Hours", "3 Hours", "Full Window"]
    )
    
    # Dynamic slot choices based on Window + Duration
    slot_options = []
    if selected_window in WINDOW_SUB_SLOTS:
        subs = WINDOW_SUB_SLOTS[selected_window]
        win_label = selected_window.split(":")[0]
        if selected_duration == "1 Hour":
            slot_options = [f"{s} (1 Hr)" for s in subs] + [f"Flexible (Any 1 hour in {win_label})"]
        elif selected_duration == "2 Hours":
            slot_options = [f"{subs[i].split(' - ')[0]} - {subs[i+1].split(' - ')[1]} (2 Hrs)" for i in range(len(subs)-1)]
            if not slot_options:
                slot_options = [f"{subs[0].split(' - ')[0]} - {subs[-1].split(' - ')[1]} (Full {win_label})"]
            slot_options.append(f"Flexible (Any 2 hours in {win_label})")
        elif selected_duration == "3 Hours":
            if len(subs) >= 3:
                slot_options = [f"{subs[i].split(' - ')[0]} - {subs[i+2].split(' - ')[1]} (3 Hrs)" for i in range(len(subs)-2)]
            else:
                slot_options = [f"{subs[0].split(' - ')[0]} - {subs[-1].split(' - ')[1]} (Full {win_label})"]
        else: # Full Window
            slot_options = [f"{subs[0].split(' - ')[0]} - {subs[-1].split(' - ')[1]} (Full {win_label})"]
    else:
        slot_options = ["Custom Hours (Specify Below)"]
        
    with st.form("creator_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Creator / Brand Name *", placeholder="e.g. RajKaran")
        handle = col2.text_input("Instagram Handle *", placeholder="e.g. @rajkaran_shoots")
        
        col3, col4 = st.columns(2)
        followers = col3.selectbox("Follower Range *", ["Under 1K", "1K – 5K", "5K – 10K", "10K – 50K", "50K+"])
        whatsapp = col4.text_input("WhatsApp Number *", value="917814259209", help="Type your 10-digit number or with country code 91.")
        
        st.markdown("---")
        shoot_type = st.selectbox(
            "What are you creating? *", 
            ["Fashion & Lifestyle", "Food & Beverage", "UGC / Brand Content", "Product Shoot", "Music / Commercial", "Other"]
        )
        description = st.text_area("Describe the shoot in one or two lines *", placeholder="e.g. Seasonal fashion lookbook shoot with 1 model")
        
        col5, col6 = st.columns(2)
        preferred_sector = col5.selectbox("Preferred Location / Sector", ["Any Sector (All Chandigarh)", "Sector 7", "Sector 8", "Sector 9", "Sector 10", "Sector 26", "Sector 35"])
        crew_size = col6.number_input("How many people on set? (Crew size) *", min_value=1, max_value=10, value=3)
        
        # Specific Slot Selector inside form
        col_slot1, col_slot2 = st.columns(2)
        chosen_slot = col_slot1.selectbox("Specific Preferred Slot Timing *", slot_options)
        custom_slot_text = ""
        if selected_window == "Custom Window / Other" or "Custom" in chosen_slot:
            custom_slot_text = col_slot2.text_input("Specify Custom Window / Timing (e.g. 01:30 PM - 03:00 PM)", placeholder="01:30 PM - 03:00 PM")
            final_slot_label = custom_slot_text if custom_slot_text else "Custom Slot"
        else:
            final_slot_label = chosen_slot
            
        col8, col9 = st.columns(2)
        needs_tripod = col8.checkbox("Tripod / Lighting Gear Required?", value=True)
        needs_natural_light = col9.checkbox("High Natural Window Light Required?", value=True)
        
        budget_pref = st.selectbox("Compensation / Deal Preference", [
            "Any (Flexible with all standard deals)",
            "Free in exchange for 1 tagged Reel", 
            "Free coffee & meal with tag", 
            "Minimum spend ₹500", 
            "Hourly fee ₹800/hr",
            "Open to Discussion"
        ])
        
        submitted = st.form_submit_button("🚀 Submit Shoot Brief to Collabé")
        if submitted:
            clean_wa = format_whatsapp_number(whatsapp)
            if not name or not handle or not clean_wa or not description:
                st.error("Please fill all required fields (*) with a valid WhatsApp phone number.")
            else:
                atomic_hours = get_atomic_hours_for_selection(selected_window, selected_duration, final_slot_label)
                new_creator = {
                    "id": f"creator_{len(st.session_state.creators)+1}",
                    "name": name,
                    "handle": handle,
                    "followers": followers,
                    "whatsapp": clean_wa,
                    "shoot_type": shoot_type,
                    "description": description,
                    "preferred_sector": preferred_sector,
                    "preferred_window": selected_window,
                    "duration": selected_duration,
                    "preferred_slot": final_slot_label,
                    "slot_hours": atomic_hours,
                    "crew_size": crew_size,
                    "needs_tripod": needs_tripod,
                    "needs_natural_light": needs_natural_light,
                    "budget_pref": budget_pref,
                    "status": "Pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.creators.append(new_creator)
                save_data(CREATORS_FILE, st.session_state.creators)
                st.success(f"🎉 Shoot brief submitted to Collabé! Selected Slot: {final_slot_label} ({selected_duration}). You will receive matching café passes directly on WhatsApp.")

# ----------------- PAGE: CAFÉ PUBLIC FORM -----------------
elif page in ["☕ Café & Venue Setup", "☕ Café & Venue Setup (Public)"]:
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Café & Restaurant Venue Registration</div>', unsafe_allow_html=True)
    
    st.info("💡 **Dead-Hour Windows**: Select all quiet morning and afternoon windows available for shoots. Creators can book 1 hour or multiple hours without blocking the rest of your window!")
    
    with st.form("cafe_form"):
        col1, col2 = st.columns(2)
        cafe_name = col1.text_input("Café / Venue Name *", placeholder="e.g. The Willow Café")
        sector = col2.selectbox("Location / Sector *", ["Sector 7", "Sector 8", "Sector 9", "Sector 10", "Sector 26", "Sector 35"])
        
        col3, col4 = st.columns(2)
        manager_phone = col3.text_input("Manager WhatsApp Number *", value="917814259209", help="Type 10-digit number or with country code 91.")
        max_crew = col4.number_input("Maximum Crew Permitted *", min_value=1, max_value=15, value=4)
        
        slots = st.multiselect(
            "Select all quiet dead-hour windows available for shoots *",
            WINDOW_OPTIONS,
            default=[
                "Morning Window: 08:00 AM to 12:00 PM",
                "Early Afternoon: 12:00 PM to 03:00 PM",
                "Afternoon Window: 03:00 PM to 06:00 PM"
            ]
        )
        
        custom_window_input = st.text_input("➕ Have Custom Dead Hours? Enter here (e.g. 11:30 AM to 02:30 PM):", placeholder="11:30 AM to 02:30 PM")
        
        col5, col6 = st.columns(2)
        allows_tripod = col5.checkbox("Allow Tripods & Ring Lights?", value=True)
        has_natural_light = col6.checkbox("Ample Natural Window Light?", value=True)
        
        deal_type = st.selectbox(
            "Deal Model Offered to Creators",
            [
                "Any (Flexible with all standard deals)",
                "Free in exchange for 1 tagged Reel", 
                "Free coffee & meal with tag", 
                "Minimum spend ₹500", 
                "Hourly fee ₹800/hr",
                "Open to Discussion"
            ]
        )
        
        if st.form_submit_button("🏪 Register Café on Collabé"):
            clean_mgr_phone = format_whatsapp_number(manager_phone)
            final_slots = list(slots)
            if custom_window_input.strip():
                final_slots.append(f"Custom Window: {custom_window_input.strip()}")
                
            if not cafe_name or not clean_mgr_phone or not final_slots:
                st.error("Please fill all required venue details with a valid phone number and at least one dead-hour window.")
            else:
                new_cafe = {
                    "id": f"cafe_{len(st.session_state.cafes)+1}",
                    "name": cafe_name,
                    "sector": sector,
                    "slots": final_slots,
                    "max_crew": max_crew,
                    "allows_tripod": allows_tripod,
                    "has_natural_light": has_natural_light,
                    "allowed_shoots": ["Food & Beverage", "Fashion & Lifestyle", "UGC / Brand Content"],
                    "deal_type": deal_type,
                    "manager_phone": clean_mgr_phone
                }
                st.session_state.cafes.append(new_cafe)
                save_data(CAFES_FILE, st.session_state.cafes)
                st.success(f"🎉 {cafe_name} successfully registered on Collabé! We will send you verified creator shoot requests for your quiet hours.")

# ----------------- PAGE: CHECK MY BOOKING STATUS (PUBLIC) -----------------
elif page == "🔍 Check My Booking Status":
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Check Your Confirmed Shoot Pass</div>', unsafe_allow_html=True)
    
    phone_search = st.text_input("Enter your WhatsApp Number to check your pass:", value="917814259209", placeholder="e.g. 7814259209")
    if phone_search:
        search_norm = format_whatsapp_number(phone_search)
        user_bookings = [b for b in st.session_state.bookings if format_whatsapp_number(b.get("creator_phone", "")) == search_norm]
        if user_bookings:
            for b in user_bookings:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: white;">🎟️ Official Shoot Pass: {b['booking_id']}</h3>
                    <p style="margin-top: 8px; margin-bottom: 4px;"><b>Venue:</b> {b['cafe_name']} ({b['sector']})</p>
                    <p style="margin-bottom: 4px;"><b>Slot:</b> {b['slot']} | <b>Window:</b> {b.get('window', 'Dead Hours')} | <b>Deal:</b> {b['deal']}</p>
                    <p style="margin-bottom: 0px;"><b>Status:</b> Confirmed & Locked ✅</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active bookings found for this number yet. Once a match is confirmed, your pass will appear here.")

# ----------------- ADMIN PAGE: LIVE MATCHING & REAL-TIME BOOKING -----------------
elif page == "⚡ Live Matching & Real-Time Booking (Admin)":
    st.markdown('<div class="brand-header">Collabé — Admin Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live Matching Algorithm, Hourly Slot Locks & WhatsApp Dispatch Desk</div>', unsafe_allow_html=True)
    
    if not st.session_state.creators:
        st.warning("No creator briefs submitted yet.")
    else:
        st.markdown("### 1️⃣ Select Creator Profile to Match:")
        creator_keys = {
            f"{c['name']} ({c['handle']}) — Wants: {c['preferred_slot']} in {c['preferred_sector']}": c 
            for c in st.session_state.creators
        }
        selected_key = st.selectbox("Choose Creator / Brand:", list(creator_keys.keys()))
        current_creator = creator_keys[selected_key]
        
        with st.expander(f"📋 Shoot Brief for {current_creator['name']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Shoot Type:** {current_creator['shoot_type']}")
            c1.write(f"**Crew Size:** {current_creator['crew_size']} people")
            c2.write(f"**Requested Slot:** `{current_creator['preferred_slot']}`")
            c2.write(f"**Window & Duration:** {current_creator.get('preferred_window', 'N/A')} ({current_creator.get('duration', '1 Hr')})")
            c3.write(f"**Needs Tripod:** {'Yes' if current_creator['needs_tripod'] else 'No'}")
            c3.write(f"**WhatsApp:** +{current_creator['whatsapp']}")

        st.markdown("---")
        st.markdown("### 2️⃣ Live Matching & Hourly Slot Availability:")
        
        has_any_match = False
        
        for cafe in st.session_state.cafes:
            status, score, reasons, open_sub_slots = evaluate_match_with_slots(current_creator, cafe)
            
            # CASE A: AVAILABLE
            if status == "AVAILABLE":
                has_any_match = True
                chips_html = "".join([f'<span class="hour-chip-free">{h}</span>' for h in open_sub_slots])
                
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #03543f;">🟢 {cafe['name']} — {cafe['sector']}</h3>
                        <span class="badge-success">Slot Available & Ready to Book! (Score: {score}/100)</span>
                    </div>
                    <p style="margin-top: 8px; margin-bottom: 5px;">
                        <b>Requested Slot:</b> <code>{current_creator['preferred_slot']}</code> (AVAILABLE ✅) &nbsp;|&nbsp;
                        <b>Max Crew:</b> {cafe['max_crew']} &nbsp;|&nbsp; 
                        <b>Deal:</b> {cafe['deal_type']}
                    </p>
                    <p style="margin-bottom: 0px; color: #444;">
                        <b>Remaining Open Hours in this Window:</b> {chips_html if chips_html else 'All Window Open'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 3])
                
                btn_key = f"book_{current_creator['id']}_{cafe['id']}"
                if col_btn1.button(f"🤝 Accept & Lock Slot ({cafe['name']})", key=btn_key):
                    creator_hours = current_creator.get("slot_hours", [])
                    if not creator_hours:
                        creator_hours = get_atomic_hours_for_selection(
                            current_creator.get("preferred_window", ""),
                            current_creator.get("duration", "1 Hour"),
                            current_creator["preferred_slot"]
                        )
                    booked_map = get_booked_hours_by_cafe()
                    cafe_booked = booked_map.get(cafe["id"], set())
                    clash = [h for h in creator_hours if h in cafe_booked]
                    
                    if clash:
                        st.error(f"❌ Race condition! Another creator just locked '{', '.join(clash)}'. Please choose remaining open hours.")
                    else:
                        booking_record = {
                            "booking_id": f"CLB_{datetime.now().strftime('%m%d_%H%M%S')}",
                            "creator_id": current_creator["id"],
                            "creator_name": current_creator["name"],
                            "creator_handle": current_creator["handle"],
                            "creator_phone": current_creator["whatsapp"],
                            "cafe_id": cafe["id"],
                            "cafe_name": cafe["name"],
                            "sector": cafe["sector"],
                            "window": current_creator.get("preferred_window", "Dead Hours Window"),
                            "duration": current_creator.get("duration", "1 Hour"),
                            "slot": current_creator["preferred_slot"],
                            "hours": creator_hours,
                            "deal": cafe["deal_type"],
                            "confirmed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "status": "Confirmed & Locked on Collabé 🔒"
                        }
                        st.session_state.bookings.append(booking_record)
                        save_data(BOOKINGS_FILE, st.session_state.bookings)
                        st.toast(f"Slot Locked on Collabé for {current_creator['name']} at {cafe['name']}!", icon="🎉")
                        st.rerun()
                        
                msg_text, wa_url = generate_whatsapp_message(
                    current_creator, 
                    cafe, 
                    current_creator['preferred_slot'], 
                    current_creator.get('duration', '1 Hour')
                )
                col_btn2.link_button("📲 Send WhatsApp Alert", wa_url)
                
                with col_btn3.expander("Preview WhatsApp Notification"):
                    st.code(msg_text, language="text")

            # CASE B: SLOT BOOKED
            elif status == "SLOT_TAKEN":
                has_any_match = True
                
                cafe_bookings = [b for b in st.session_state.bookings if b.get("cafe_id") == cafe["id"]]
                my_booking = next((b for b in cafe_bookings if b.get("creator_id") == current_creator["id"]), None)
                
                if my_booking:
                    st.balloons()
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 12px; padding: 22px; margin-bottom: 20px;">
                        <h2 style="margin: 0; color: white;">🎟️ Shoot Booking Confirmed & Locked!</h2>
                        <span style="background: white; color: #065f46; padding: 6px 14px; border-radius: 20px; font-weight: 700;">
                            Pass ID: {my_booking['booking_id']}
                        </span>
                        <p style="font-size: 1.1rem; margin-top: 10px; margin-bottom: 5px;">
                            <b>Venue:</b> {cafe['name']} ({cafe['sector']}) | <b>Slot:</b> {my_booking['slot']} ({my_booking.get('duration', '1 Hr')})
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 1])
                    mgr_msg = (
                        f"Hello {cafe['name']} Management! 🎬 (via Collabé)\n\n"
                        f"Great news! Creator {current_creator['name']} ({current_creator['handle']}, {current_creator['followers']} followers) has confirmed and locked the shoot slot on Collabé!\n\n"
                        f"🎟️ Booking ID: {my_booking['booking_id']}\n"
                        f"🕒 Slot: {my_booking['slot']} ({my_booking.get('duration', '1 Hr')})\n"
                        f"👥 Crew Size: {current_creator['crew_size']} people\n"
                        f"📸 Shoot: {current_creator['description']}\n"
                        f"💡 Agreed Deal: {cafe['deal_type']}\n"
                        f"📷 Gear: {'Tripod' if current_creator['needs_tripod'] else 'Phone/Handheld'}\n"
                        f"📞 Creator Contact: +{current_creator['whatsapp']}\n\n"
                        f"Please ensure a designated table is ready for the creator."
                    )
                    mgr_url = f"https://wa.me/{cafe['manager_phone']}?text={urllib.parse.quote(mgr_msg)}"
                    col_act1.link_button("📲 Notify Café Manager", mgr_url)
                    
                    creator_pass_msg = (
                        f"🎉 OFFICIAL SHOOT PASS — Collabé 🎬\n\n"
                        f"Hi {current_creator['name']}! Your shoot is confirmed and locked in the schedule.\n\n"
                        f"📍 Venue: {cafe['name']}, {cafe['sector']}\n"
                        f"🎟️ Booking Pass ID: {my_booking['booking_id']}\n"
                        f"🕒 Confirmed Slot: {my_booking['slot']} ({my_booking.get('duration', '1 Hr')})\n"
                        f"👥 Crew Size Allowed: Up to {cafe['max_crew']} people\n"
                        f"💡 Agreed Deal: {cafe['deal_type']}\n"
                        f"📷 Rules: {'Tripods Allowed ✅' if cafe['allows_tripod'] else 'No Tripods ❌'} | {'Natural Light Available ✅' if cafe['has_natural_light'] else 'Indoor Light'}\n"
                        f"📞 Venue Manager Phone: +{cafe['manager_phone']}\n\n"
                        f"⚡ On Arrival: Show this WhatsApp pass to the café manager or staff at the counter to access your reserved area.\n\n"
                        f"Have a great shoot!"
                    )
                    pass_url = f"https://wa.me/{current_creator['whatsapp']}?text={urllib.parse.quote(creator_pass_msg)}"
                    col_act2.link_button("📲 Send Pass to Creator", pass_url)
                    
                    if col_act3.button("❌ Release Slot", key=f"cancel_{my_booking['booking_id']}"):
                        st.session_state.bookings = [b for b in st.session_state.bookings if b["booking_id"] != my_booking["booking_id"]]
                        save_data(BOOKINGS_FILE, st.session_state.bookings)
                        st.toast("Slot reopened for other creators!", icon="🔄")
                        st.rerun()

                else:
                    conflicting_booking = cafe_bookings[0] if cafe_bookings else None
                    other_creator = conflicting_booking.get("creator_name", "another creator") if conflicting_booking else "another creator"
                    chips_html = "".join([f'<span class="hour-chip-free">{h}</span>' for h in open_sub_slots])
                    
                    st.markdown(f"""
                    <div class="slot-taken-card">
                        <h3 style="margin: 0; color: #9b1c1c;">🔴 {cafe['name']} — {cafe['sector']}</h3>
                        <p style="color: #771d1d; margin-top: 5px;">
                            Slot <code>{current_creator['preferred_slot']}</code> is <b>UNAVAILABLE ❌</b> because {other_creator} booked this hour first.
                        </p>
                        <p style="margin-bottom: 0px; color: #333;">
                            <b>Still Open in this Window at this Café:</b> {chips_html if chips_html else 'No remaining hours in this window'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            # CASE C: INCOMPATIBLE
            else:
                with st.expander(f"⚪ Incompatible: {cafe['name']} ({cafe['sector']})"):
                    for r in reasons:
                        st.write(f"• {r}")

# ----------------- ADMIN PAGE: LIVE TABULAR DATA -----------------
elif page == "📊 Live Tabular Data & Slot Status (Admin)":
    st.markdown('<div class="brand-header">Collabé — Database Admin</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Internal Data Tables & Real-Time Hourly Slot Inventory</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤝 Confirmed Bookings", "☕ Cafés & Dead-Hour Inventory", "📝 Creator Briefs"])
    
    with tab1:
        st.markdown(f"**Total Confirmed Bookings:** {len(st.session_state.bookings)}")
        if st.session_state.bookings:
            df_b = pd.DataFrame(st.session_state.bookings)
            st.dataframe(df_b, width='stretch')
        else:
            st.info("No bookings confirmed yet.")
            
    with tab2:
        st.markdown("**Hourly Dead-Hour Inventory per Café:**")
        cafe_status_list = []
        booked_map = get_booked_hours_by_cafe()
        for c in st.session_state.cafes:
            b_hours = list(booked_map.get(c["id"], []))
            
            # Compute total free hours
            all_possible_hours = []
            for win in c["slots"]:
                if win in WINDOW_SUB_SLOTS:
                    all_possible_hours.extend(WINDOW_SUB_SLOTS[win])
                else:
                    all_possible_hours.append(win)
            # Remove duplicates preserving order
            seen_h = set()
            dedup_hours = []
            for h in all_possible_hours:
                if h not in seen_h:
                    seen_h.add(h)
                    dedup_hours.append(h)
                    
            free_hours = [h for h in dedup_hours if h not in b_hours]
            
            cafe_status_list.append({
                "Café Name": c["name"],
                "Sector": c["sector"],
                "Dead-Hour Windows": ", ".join(c["slots"]),
                "Booked Hours": ", ".join(b_hours) if b_hours else "None (0 Hrs)",
                "Still Free & Available": ", ".join(free_hours) if free_hours else "Fully Booked ❌",
                "Max Crew": c["max_crew"],
                "Deal Model": c["deal_type"],
                "Manager Phone": c["manager_phone"]
            })
        st.dataframe(pd.DataFrame(cafe_status_list), width='stretch')
        
    with tab3:
        st.dataframe(pd.DataFrame(st.session_state.creators), width='stretch')
