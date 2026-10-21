import streamlit as st  # type: ignore  # pyrefly: ignore[missing-import]
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
    .hour-chip-free {
        display: inline-block;
        background: #ecfdf5;
        color: #065f46;
        padding: 3px 9px;
        border-radius: 5px;
        margin: 2px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #a7f3d0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- DURATION-BASED SLOTS SELECTION MAP -----------------
DURATION_SLOT_MAP = {
    "1 Hour": [
        "Morning: 08:00 AM - 09:00 AM (1 Hr)",
        "Morning: 09:00 AM - 10:00 AM (1 Hr)",
        "Morning: 10:00 AM - 11:00 AM (1 Hr)",
        "Morning: 11:00 AM - 12:00 PM (1 Hr)",
        "Afternoon: 12:00 PM - 01:00 PM (1 Hr)",
        "Afternoon: 01:00 PM - 02:00 PM (1 Hr)",
        "Afternoon: 02:00 PM - 03:00 PM (1 Hr)",
        "Afternoon: 03:00 PM - 04:00 PM (1 Hr)",
        "Afternoon: 04:00 PM - 05:00 PM (1 Hr)",
        "Afternoon: 05:00 PM - 06:00 PM (1 Hr)",
        "Evening: 06:00 PM - 07:00 PM (1 Hr)",
        "Custom 1-Hour Slot (Specify Below)"
    ],
    "2 Hours": [
        "Morning: 08:00 AM - 10:00 AM (2 Hrs)",
        "Morning: 09:00 AM - 11:00 AM (2 Hrs)",
        "Morning: 10:00 AM - 12:00 PM (2 Hrs)",
        "Afternoon: 12:00 PM - 02:00 PM (2 Hrs)",
        "Afternoon: 01:00 PM - 03:00 PM (2 Hrs)",
        "Afternoon: 02:00 PM - 04:00 PM (2 Hrs)",
        "Afternoon: 03:00 PM - 05:00 PM (2 Hrs)",
        "Afternoon: 04:00 PM - 06:00 PM (2 Hrs)",
        "Evening: 05:00 PM - 07:00 PM (2 Hrs)",
        "Custom 2-Hour Slot (Specify Below)"
    ],
    "3 Hours": [
        "Morning: 08:00 AM - 11:00 AM (3 Hrs)",
        "Morning: 09:00 AM - 12:00 PM (3 Hrs)",
        "Afternoon: 12:00 PM - 03:00 PM (3 Hrs)",
        "Afternoon: 01:00 PM - 04:00 PM (3 Hrs)",
        "Afternoon: 02:00 PM - 05:00 PM (3 Hrs)",
        "Afternoon: 03:00 PM - 06:00 PM (3 Hrs)",
        "Custom 3-Hour Slot (Specify Below)"
    ],
    "Full Window (3-4 Hours)": [
        "Morning Window: 08:00 AM to 12:00 PM (4 Hrs)",
        "Early Afternoon Window: 12:00 PM to 03:00 PM (3 Hrs)",
        "Afternoon Window: 03:00 PM to 06:00 PM (3 Hrs)",
        "Evening Window: 05:00 PM to 08:00 PM (3 Hrs)",
        "Custom Full Window (Specify Below)"
    ],
    "Custom Duration": [
        "Custom Timing (Specify Below)"
    ]
}

# Maps each slot to its atomic 1-hour building blocks
SLOT_TO_HOURS = {
    # 1 Hour
    "Morning: 08:00 AM - 09:00 AM (1 Hr)": ["08:00 AM - 09:00 AM"],
    "Morning: 09:00 AM - 10:00 AM (1 Hr)": ["09:00 AM - 10:00 AM"],
    "Morning: 10:00 AM - 11:00 AM (1 Hr)": ["10:00 AM - 11:00 AM"],
    "Morning: 11:00 AM - 12:00 PM (1 Hr)": ["11:00 AM - 12:00 PM"],
    "Afternoon: 12:00 PM - 01:00 PM (1 Hr)": ["12:00 PM - 01:00 PM"],
    "Afternoon: 01:00 PM - 02:00 PM (1 Hr)": ["01:00 PM - 02:00 PM"],
    "Afternoon: 02:00 PM - 03:00 PM (1 Hr)": ["02:00 PM - 03:00 PM"],
    "Afternoon: 03:00 PM - 04:00 PM (1 Hr)": ["03:00 PM - 04:00 PM"],
    "Afternoon: 04:00 PM - 05:00 PM (1 Hr)": ["04:00 PM - 05:00 PM"],
    "Afternoon: 05:00 PM - 06:00 PM (1 Hr)": ["05:00 PM - 06:00 PM"],
    "Evening: 06:00 PM - 07:00 PM (1 Hr)": ["06:00 PM - 07:00 PM"],

    # 2 Hours
    "Morning: 08:00 AM - 10:00 AM (2 Hrs)": ["08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM"],
    "Morning: 09:00 AM - 11:00 AM (2 Hrs)": ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM"],
    "Morning: 10:00 AM - 12:00 PM (2 Hrs)": ["10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM"],
    "Afternoon: 12:00 PM - 02:00 PM (2 Hrs)": ["12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM"],
    "Afternoon: 01:00 PM - 03:00 PM (2 Hrs)": ["01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM"],
    "Afternoon: 02:00 PM - 04:00 PM (2 Hrs)": ["02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM"],
    "Afternoon: 03:00 PM - 05:00 PM (2 Hrs)": ["03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"],
    "Afternoon: 04:00 PM - 06:00 PM (2 Hrs)": ["04:00 PM - 05:00 PM", "05:00 PM - 06:00 PM"],
    "Evening: 05:00 PM - 07:00 PM (2 Hrs)": ["05:00 PM - 06:00 PM", "06:00 PM - 07:00 PM"],

    # 3 Hours
    "Morning: 08:00 AM - 11:00 AM (3 Hrs)": ["08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM"],
    "Morning: 09:00 AM - 12:00 PM (3 Hrs)": ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM"],
    "Afternoon: 12:00 PM - 03:00 PM (3 Hrs)": ["12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM"],
    "Afternoon: 01:00 PM - 04:00 PM (3 Hrs)": ["01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM"],
    "Afternoon: 02:00 PM - 05:00 PM (3 Hrs)": ["02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"],
    "Afternoon: 03:00 PM - 06:00 PM (3 Hrs)": ["03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM", "05:00 PM - 06:00 PM"],

    # Full Windows
    "Morning Window: 08:00 AM to 12:00 PM (4 Hrs)": [
        "08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM"
    ],
    "Early Afternoon Window: 12:00 PM to 03:00 PM (3 Hrs)": [
        "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM"
    ],
    "Afternoon Window: 03:00 PM to 06:00 PM (3 Hrs)": [
        "03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM", "05:00 PM - 06:00 PM"
    ],
    "Evening Window: 05:00 PM to 08:00 PM (3 Hrs)": [
        "05:00 PM - 06:00 PM", "06:00 PM - 07:00 PM", "07:00 PM - 08:00 PM"
    ]
}

# Broad dead-hour windows that Cafés can select
CAFE_WINDOW_OPTIONS = [
    "Morning Window: 08:00 AM to 12:00 PM",
    "Early Afternoon: 12:00 PM to 03:00 PM",
    "Afternoon Window: 03:00 PM to 06:00 PM",
    "Morning (8 AM - 10 AM)",
    "Morning (10 AM - 12 PM)",
    "Afternoon (12 PM - 3 PM)",
    "Afternoon (3 PM - 5 PM)",
    "Evening (5 PM - 7 PM)",
    "Early Morning: 07:00 AM to 09:00 AM",
    "Late Evening: 08:00 PM to 10:00 PM"
]

CAFE_WINDOW_TO_HOURS = {
    "Morning Window: 08:00 AM to 12:00 PM": ["08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM"],
    "Early Afternoon: 12:00 PM to 03:00 PM": ["12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM"],
    "Afternoon Window: 03:00 PM to 06:00 PM": ["03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM", "05:00 PM - 06:00 PM"],
    "Morning (8 AM - 10 AM)": ["08:00 AM - 09:00 AM", "09:00 AM - 10:00 AM"],
    "Morning (10 AM - 12 PM)": ["10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM"],
    "Afternoon (12 PM - 3 PM)": ["12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM"],
    "Afternoon (3 PM - 5 PM)": ["03:00 PM - 04:00 PM", "04:00 PM - 05:00 PM"],
    "Evening (5 PM - 7 PM)": ["05:00 PM - 06:00 PM", "06:00 PM - 07:00 PM"],
    "Early Morning: 07:00 AM to 09:00 AM": ["07:00 AM - 08:00 AM", "08:00 AM - 09:00 AM"],
    "Late Evening: 08:00 PM to 10:00 PM": ["08:00 PM - 09:00 PM", "09:00 PM - 10:00 PM"]
}

def get_atomic_hours_for_creator_slot(slot_str):
    """Returns the list of 1-hour atomic blocks for a creator's slot."""
    if slot_str in SLOT_TO_HOURS:
        return SLOT_TO_HOURS[slot_str]
    for k, v in SLOT_TO_HOURS.items():
        if k in slot_str or slot_str in k:
            return v
    return [slot_str]

def get_all_hours_for_cafe(cafe):
    """Returns the set of all 1-hour atomic blocks hosted by a cafe across its listed slots."""
    hours = set()
    for w in cafe.get("slots", []):
        if w in CAFE_WINDOW_TO_HOURS:
            hours.update(CAFE_WINDOW_TO_HOURS[w])
        elif w in SLOT_TO_HOURS:
            hours.update(SLOT_TO_HOURS[w])
        else:
            hours.add(w)
    return hours

# ----------------- DATA PERSISTENCE LAYER -----------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CAFES_FILE = os.path.join(DATA_DIR, "cafes.json")
CREATORS_FILE = os.path.join(DATA_DIR, "creators.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")

# Pre-seeded Chandigarh Cafés with Morning and Afternoon dead-hour windows
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

# Starter creators across Morning and Afternoon slots
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
        "duration": "1 Hour",
        "preferred_slot": "Morning: 08:00 AM - 09:00 AM (1 Hr)",
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
        "duration": "2 Hours",
        "preferred_slot": "Morning: 09:00 AM - 11:00 AM (2 Hrs)",
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
        "duration": "1 Hour",
        "preferred_slot": "Afternoon: 01:00 PM - 02:00 PM (1 Hr)",
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
        "description": "Golden hour casual lifestyle shoot",
        "preferred_sector": "Sector 9",
        "duration": "2 Hours",
        "preferred_slot": "Afternoon: 03:00 PM - 05:00 PM (2 Hrs)",
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
            inferred = get_atomic_hours_for_creator_slot(b.get("slot", ""))
            for h in inferred:
                booked_map[cid].add(h)
    return booked_map

def clean_indian_phone(phone_str):
    """Extracts 10 digits and prepends 91 country code automatically."""
    digits = "".join(filter(str.isdigit, str(phone_str)))
    if len(digits) >= 10:
        return "91" + digits[-10:]
    return ""

def get_open_hours_for_cafe_and_slot(cafe, creator_slot):
    """Returns all open hours at this cafe."""
    cafe_hours = get_all_hours_for_cafe(cafe)
    booked_map = get_booked_hours_by_cafe()
    cafe_booked = booked_map.get(cafe["id"], set())
    return [h for h in sorted(list(cafe_hours)) if h not in cafe_booked]

# ----------------- MATCHING ENGINE -----------------
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
    creator_hours = creator.get("slot_hours", [])
    if not creator_hours:
        creator_hours = get_atomic_hours_for_creator_slot(creator.get("preferred_slot", ""))
        
    cafe_hours = get_all_hours_for_cafe(cafe)
    
    # Check if cafe hosts all requested hours
    hours_offered = all(h in cafe_hours for h in creator_hours)
    if not hours_offered:
        slot_label = creator.get("preferred_slot", "")
        window_match = any(slot_label in cs or cs in slot_label for cs in cafe["slots"])
        if not window_match:
            failed_reasons.append(f"Café does not host shoots during requested time ({slot_label})")
        
    # 5. Atomic Hourly Slot Conflict Check
    booked_map = get_booked_hours_by_cafe()
    cafe_booked = booked_map.get(cafe["id"], set())
    
    conflicting_hours = [h for h in creator_hours if h in cafe_booked]
    open_sub_slots = get_open_hours_for_cafe_and_slot(cafe, creator.get("preferred_slot", ""))
    
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

def generate_whatsapp_message(creator, cafe, slot):
    msg = (
        f"Hi {creator['name']}! 🎬 (via Collabé)\n\n"
        f"We found a verified shoot match in Chandigarh for your brief:\n\n"
        f"📍 Venue: {cafe['name']} ({cafe['sector']})\n"
        f"🕒 Available Slot: {slot}\n"
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
    
    st.info("💡 **Dynamic Hourly Slot Booking**: First pick the duration you need (1 Hour, 2 Hours, 3 Hours, etc.). The slot dropdown will automatically show matching morning and afternoon options for that duration!")
    
    col1, col2 = st.columns(2)
    name = col1.text_input("Creator / Brand Name *", placeholder="e.g. RajKaran", key="c_name")
    handle = col2.text_input("Instagram Handle *", placeholder="e.g. @rajkaran_shoots", key="c_handle")
    
    col3, col4_code, col4_num = st.columns([2, 1, 3])
    followers = col3.selectbox("Follower Range *", ["Under 1K", "1K – 5K", "5K – 10K", "10K – 50K", "50K+"], key="c_folls")
    col4_code.text_input("Country Code", value="+91 (India)", disabled=True, key="c_code")
    whatsapp_input = col4_num.text_input("WhatsApp Number (10 Digits) *", value="7814259209", max_chars=10, placeholder="7814259209", key="c_num")
    
    st.markdown("---")
    shoot_type = st.selectbox(
        "What are you creating? *", 
        ["Fashion & Lifestyle", "Food & Beverage", "UGC / Brand Content", "Product Shoot", "Music / Commercial", "Other"],
        key="c_type"
    )
    description = st.text_area("Describe the shoot in one or two lines *", placeholder="e.g. Seasonal fashion lookbook shoot with 1 model", key="c_desc")
    
    col5, col6 = st.columns([1.5, 1])
    preferred_sector = col5.selectbox("Preferred Location / Sector", ["Any Sector (All Chandigarh)", "Sector 7", "Sector 8", "Sector 9", "Sector 10", "Sector 26", "Sector 35"], key="c_sec")
    crew_size = col6.number_input("Crew Size (People on set) *", min_value=1, max_value=10, value=3, key="c_crew")
    
    st.markdown("---")
    st.markdown("##### ⏱️ **Shoot Duration & Timing Selection**")
    
    col_dur, col_slot = st.columns([1, 2])
    duration_choice = col_dur.selectbox(
        "1. Select Duration Needed *",
        ["1 Hour", "2 Hours", "3 Hours", "Full Window (3-4 Hours)", "Custom Duration"],
        index=0,
        key="c_duration_picker"
    )
    
    matching_slots = DURATION_SLOT_MAP.get(duration_choice, [])
    preferred_slot = col_slot.selectbox(
        f"2. Available Slots for {duration_choice} *",
        matching_slots,
        key="c_slot_picker"
    )
    
    custom_slot_text = ""
    if "Custom" in preferred_slot or duration_choice == "Custom Duration":
        custom_slot_text = st.text_input("Enter your preferred custom timing (e.g. 11:30 AM - 01:00 PM):", placeholder="11:30 AM - 01:00 PM", key="c_custom")
        final_slot = custom_slot_text if custom_slot_text.strip() else "Custom Timing"
    else:
        final_slot = preferred_slot
        
    col8, col9 = st.columns(2)
    needs_tripod = col8.checkbox("Tripod / Lighting Gear Required?", value=True, key="c_tripod")
    needs_natural_light = col9.checkbox("High Natural Window Light Required?", value=True, key="c_light")
    
    budget_pref = st.selectbox("Compensation / Deal Preference", [
        "Any (Flexible with all standard deals)",
        "Free in exchange for 1 tagged Reel", 
        "Free coffee & meal with tag", 
        "Minimum spend ₹500", 
        "Hourly fee ₹800/hr",
        "Open to Discussion"
    ], key="c_deal")
    
    if st.button("🚀 Submit Shoot Brief to Collabé", type="primary"):
        clean_wa = clean_indian_phone(whatsapp_input)
        if not name or not handle or not clean_wa or not description or len(clean_wa) != 12:
            st.error("Please fill all required fields (*) with a valid 10-digit WhatsApp phone number.")
        else:
            atomic_hours = get_atomic_hours_for_creator_slot(final_slot)
            new_creator = {
                "id": f"creator_{len(st.session_state.creators)+1}",
                "name": name,
                "handle": handle,
                "followers": followers,
                "whatsapp": clean_wa,
                "shoot_type": shoot_type,
                "description": description,
                "preferred_sector": preferred_sector,
                "duration": duration_choice,
                "preferred_slot": final_slot,
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
            st.success(f"🎉 Shoot brief submitted to Collabé! Selected Slot: {final_slot} ({duration_choice}). Matching café passes will be dispatched directly to your WhatsApp (+{clean_wa}).")

# ----------------- PAGE: CAFÉ PUBLIC FORM -----------------
elif page in ["☕ Café & Venue Setup", "☕ Café & Venue Setup (Public)"]:
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Café & Restaurant Venue Registration</div>', unsafe_allow_html=True)
    
    st.info("💡 **Dead-Hour Windows**: Select all quiet morning and afternoon windows available for shoots. Creators can book 1 hour without blocking the rest of your window!")
    
    with st.form("cafe_form"):
        col1, col2 = st.columns(2)
        cafe_name = col1.text_input("Café / Venue Name *", placeholder="e.g. The Willow Café")
        sector = col2.selectbox("Location / Sector *", ["Sector 7", "Sector 8", "Sector 9", "Sector 10", "Sector 26", "Sector 35"])
        
        col3_code, col3_num, col4 = st.columns([1, 2, 2])
        col3_code.text_input("Country Code ", value="+91 (India)", disabled=True)
        manager_phone_input = col3_num.text_input("Manager WhatsApp (10 Digits) *", value="7814259209", max_chars=10, placeholder="7814259209")
        max_crew = col4.number_input("Maximum Crew Permitted *", min_value=1, max_value=15, value=4)
        
        slots = st.multiselect(
            "Select all quiet dead-hour windows available for shoots *",
            CAFE_WINDOW_OPTIONS,
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
            clean_mgr_phone = clean_indian_phone(manager_phone_input)
            final_slots = list(slots)
            if custom_window_input.strip():
                final_slots.append(f"Custom Window: {custom_window_input.strip()}")
                
            if not cafe_name or not clean_mgr_phone or not final_slots or len(clean_mgr_phone) != 12:
                st.error("Please fill all required venue details with a valid 10-digit phone number and at least one dead-hour window.")
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
    
    col_s1, col_s2 = st.columns([1, 4])
    col_s1.text_input("Country Code", value="+91", disabled=True, key="search_code")
    phone_search = col_s2.text_input("Enter your 10-digit WhatsApp Number to check your pass:", value="7814259209", max_chars=10, placeholder="7814259209")
    if phone_search:
        search_norm = clean_indian_phone(phone_search)
        user_bookings = [b for b in st.session_state.bookings if clean_indian_phone(b.get("creator_phone", "")) == search_norm]
        if user_bookings:
            for b in user_bookings:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: white;">🎟️ Official Shoot Pass: {b['booking_id']}</h3>
                    <p style="margin-top: 8px; margin-bottom: 4px;"><b>Venue:</b> {b['cafe_name']} ({b['sector']})</p>
                    <p style="margin-bottom: 4px;"><b>Slot:</b> {b['slot']} | <b>Deal:</b> {b['deal']}</p>
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
            c2.write(f"**Duration:** {current_creator.get('duration', '1 Hour')}")
            c3.write(f"**Location:** {current_creator['preferred_sector']}")
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
                        <b>Open Hours at this Café:</b> {chips_html if chips_html else 'All Window Open'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 3])
                
                btn_key = f"book_{current_creator['id']}_{cafe['id']}"
                if col_btn1.button(f"🤝 Accept & Lock Slot ({cafe['name']})", key=btn_key):
                    creator_hours = current_creator.get("slot_hours", [])
                    if not creator_hours:
                        creator_hours = get_atomic_hours_for_creator_slot(current_creator["preferred_slot"])
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
                    current_creator['preferred_slot']
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
                            <b>Venue:</b> {cafe['name']} ({cafe['sector']}) | <b>Slot:</b> {my_booking['slot']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 1])
                    mgr_msg = (
                        f"Hello {cafe['name']} Management! 🎬 (via Collabé)\n\n"
                        f"Great news! Creator {current_creator['name']} ({current_creator['handle']}, {current_creator['followers']} followers) has confirmed and locked the shoot slot on Collabé!\n\n"
                        f"🎟️ Booking ID: {my_booking['booking_id']}\n"
                        f"🕒 Slot: {my_booking['slot']}\n"
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
                        f"🕒 Confirmed Slot: {my_booking['slot']}\n"
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
                            <b>Still Open at this Café:</b> {chips_html if chips_html else 'No remaining hours available'}
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
            st.dataframe(df_b, use_container_width=True)
        else:
            st.info("No bookings confirmed yet.")
            
    with tab2:
        st.markdown("**Hourly Dead-Hour Inventory per Café:**")
        cafe_status_list = []
        booked_map = get_booked_hours_by_cafe()
        for c in st.session_state.cafes:
            b_hours = list(booked_map.get(c["id"], []))
            all_possible_hours = get_all_hours_for_cafe(c)
            free_hours = [h for h in sorted(list(all_possible_hours)) if h not in b_hours]
            
            cafe_status_list.append({
                "Café Name": c["name"],
                "Sector": c["sector"],
                "Listed Windows": ", ".join(c["slots"]),
                "Booked Hours": ", ".join(b_hours) if b_hours else "None (0 Hrs)",
                "Still Free & Available": ", ".join(free_hours) if free_hours else "Fully Booked ❌",
                "Max Crew": c["max_crew"],
                "Deal Model": c["deal_type"],
                "Manager Phone": c["manager_phone"]
            })
        st.dataframe(pd.DataFrame(cafe_status_list), use_container_width=True)
        
    with tab3:
        st.dataframe(pd.DataFrame(st.session_state.creators), use_container_width=True)
