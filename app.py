import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime

# Page configuration with official brand name
st.set_page_config(
    page_title="Collabé | Creator & Café Matching Platform",
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
</style>
""", unsafe_allow_html=True)

# ----------------- DATA PERSISTENCE LAYER -----------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CAFES_FILE = os.path.join(DATA_DIR, "cafes.json")
CREATORS_FILE = os.path.join(DATA_DIR, "creators.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")

# Pre-seeded Chandigarh Cafés
INITIAL_CAFES = [
    {
        "id": "cafe_1",
        "name": "The Willow Café",
        "sector": "Sector 9",
        "slots": ["Morning (8 AM - 11 AM)", "Afternoon (3 PM - 5 PM)"],
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
        "slots": ["Morning (8 AM - 10 AM)", "Afternoon (3 PM - 5 PM)", "Evening (5 PM - 7 PM)"],
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
        "slots": ["Morning (8 AM - 10 AM)"],
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
        "slots": ["Morning (10 AM - 1 PM)", "Afternoon (2 PM - 5 PM)"],
        "max_crew": 6,
        "allows_tripod": True,
        "has_natural_light": True,
        "allowed_shoots": ["Fashion & Lifestyle", "Music / Commercial", "Product Shoot"],
        "deal_type": "Hourly fee ₹800/hr",
        "manager_phone": "917814259209"
    }
]

# Starter creators
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
        "preferred_slot": "Morning (8 AM - 11 AM)",
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
        "preferred_slot": "Morning (8 AM - 11 AM)",
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
        "preferred_slot": "Afternoon (3 PM - 5 PM)",
        "crew_size": 2,
        "needs_tripod": True,
        "needs_natural_light": True,
        "budget_pref": "Free in exchange for 1 tagged Reel",
        "status": "Pending",
        "timestamp": "2026-10-16 11:15"
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

# Always ensure fresh brand and creator data synced with disk
st.session_state.cafes = load_data(CAFES_FILE, INITIAL_CAFES)
st.session_state.creators = load_data(CREATORS_FILE, INITIAL_CREATORS)
st.session_state.bookings = load_data(BOOKINGS_FILE, [])

# ----------------- BOOKED SLOTS TRACKING -----------------
def get_booked_slots():
    booked_map = {}
    for b in st.session_state.bookings:
        cid = b.get("cafe_id")
        slot = b.get("slot")
        if cid and slot:
            if cid not in booked_map:
                booked_map[cid] = set()
            booked_map[cid].add(slot)
    return booked_map

def get_available_slots_for_cafe(cafe):
    booked_map = get_booked_slots()
    booked_for_this = booked_map.get(cafe["id"], set())
    return [s for s in cafe["slots"] if s not in booked_for_this]

# ----------------- MATCHING ENGINE -----------------
def evaluate_match_with_slots(creator, cafe):
    failed_reasons = []
    
    # 1. Hard Check: Crew Size
    if creator["crew_size"] > cafe["max_crew"]:
        failed_reasons.append(f"Crew size ({creator['crew_size']}) exceeds café limit ({cafe['max_crew']})")
    
    # 2. Hard Check: Tripod Allowed
    if creator["needs_tripod"] and not cafe["allows_tripod"]:
        failed_reasons.append("Creator needs tripod, but café does not allow tripods")
        
    # 3. Hard Check: Natural Light
    if creator["needs_natural_light"] and not cafe["has_natural_light"]:
        failed_reasons.append("Creator requires natural window light, which café lacks")
        
    # 4. Check Slot: Is this slot originally offered by café?
    if creator["preferred_slot"] not in cafe["slots"]:
        failed_reasons.append(f"Café does not host shoots during requested time ({creator['preferred_slot']})")
        
    # 5. Check Real-Time Availability: Has someone ALREADY booked this slot?
    booked_map = get_booked_slots()
    is_slot_already_taken = creator["preferred_slot"] in booked_map.get(cafe["id"], set())
    
    remaining_slots = get_available_slots_for_cafe(cafe)
    
    if failed_reasons:
        return "INCOMPATIBLE", 0, failed_reasons, remaining_slots
    
    if is_slot_already_taken:
        return "SLOT_TAKEN", 0, ["Someone has already booked this slot!"], remaining_slots
        
    # Score
    score = 75
    if creator.get("preferred_sector") == cafe["sector"]:
        score += 15
    if creator.get("budget_pref") == cafe.get("deal_type"):
        score += 10
        
    return "AVAILABLE", score, [], remaining_slots

def generate_whatsapp_message(creator, cafe, slot):
    msg = (
        f"Hi {creator['name']}! 🎬 (via Collabé)\n\n"
        f"We found a verified shoot match in Chandigarh for your brief:\n\n"
        f"📍 Venue: {cafe['name']} ({cafe['sector']})\n"
        f"🕒 Available Slot: {slot}\n"
        f"👥 Max Crew: {cafe['max_crew']} people\n"
        f"💡 Deal Model: {cafe['deal_type']}\n"
        f"📷 Tripod: {'Allowed' if cafe['allows_tripod'] else 'No'} | Light: {'Natural' if cafe['has_natural_light'] else 'Normal'}\n\n"
        f"⚠️ Note: Slots on Collabé are locked on a first-come, first-served basis. Accept now to reserve this slot before another creator books it!"
    )
    encoded = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/{creator['whatsapp']}?text={encoded}"
    return msg, wa_url

# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.markdown("## 🎬 **Collabé**")
st.sidebar.markdown("*The Creator & Café Match Network*")

page = st.sidebar.radio(
    "Navigation:",
    [
        "⚡ Live Matching & Real-Time Booking", 
        "📝 Creator / Brand Request Form", 
        "☕ Café & Venue Setup", 
        "📊 Live Tabular Data & Slot Status"
    ]
)

st.sidebar.markdown("---")
booked_map = get_booked_slots()
total_booked_count = sum(len(slots) for slots in booked_map.values())
st.sidebar.info(
    f"📊 **Collabé Live Status**\n\n"
    f"• Registered Cafés: **{len(st.session_state.cafes)}**\n"
    f"• Creator Briefs: **{len(st.session_state.creators)}**\n"
    f"• Locked Slots: **{total_booked_count}**\n"
    f"• Confirmed Bookings: **{len(st.session_state.bookings)}**"
)

# Reset demo bookings button
if st.sidebar.button("🔄 Reset Demo Bookings"):
    st.session_state.bookings = []
    save_data(BOOKINGS_FILE, [])
    st.sidebar.success("All bookings cleared! All slots are open on Collabé.")
    st.rerun()

# ----------------- PAGE 1: LIVE MATCHING & BOOKING -----------------
if page == "⚡ Live Matching & Real-Time Booking":
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live matching engine connecting content creators & small brands with aesthetic venues.</div>', unsafe_allow_html=True)
    
    if not st.session_state.creators:
        st.warning("No creator briefs submitted yet. Add one in the Creator Form!")
    else:
        st.markdown("### 1️⃣ Select Creator Profile to Match:")
        creator_keys = {f"{c['name']} ({c['handle']}) — Wants: {c['preferred_slot']} in {c['preferred_sector']}": c for c in st.session_state.creators}
        selected_key = st.selectbox("Choose Creator / Brand:", list(creator_keys.keys()))
        current_creator = creator_keys[selected_key]
        
        with st.expander(f"📋 Shoot Brief for {current_creator['name']}", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Shoot Type:** {current_creator['shoot_type']}")
            c1.write(f"**Crew Size:** {current_creator['crew_size']} people")
            c2.write(f"**Preferred Slot:** `{current_creator['preferred_slot']}`")
            c2.write(f"**Preferred Sector:** {current_creator['preferred_sector']}")
            c3.write(f"**Needs Tripod:** {'Yes' if current_creator['needs_tripod'] else 'No'}")
            c3.write(f"**WhatsApp:** {current_creator['whatsapp']}")

        st.markdown("---")
        st.markdown("### 2️⃣ Live Matching & Slot Status:")
        
        has_any_match = False
        
        for cafe in st.session_state.cafes:
            status, score, reasons, remaining_slots = evaluate_match_with_slots(current_creator, cafe)
            
            # CASE A: MATCHED & AVAILABLE
            if status == "AVAILABLE":
                has_any_match = True
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
                    <p style="margin-bottom: 0px; color: #555;">
                        <b>Other Open Slots at this Café:</b> {', '.join(remaining_slots) if remaining_slots else 'Only this slot'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 3])
                
                # Real-Time Accept Booking Button
                btn_key = f"book_{current_creator['id']}_{cafe['id']}"
                if col_btn1.button(f"🤝 Accept & Lock Slot ({cafe['name']})", key=btn_key):
                    booked_map = get_booked_slots()
                    if current_creator['preferred_slot'] in booked_map.get(cafe['id'], set()):
                        st.error(f"❌ Someone just booked this slot a moment ago! Slot '{current_creator['preferred_slot']}' is no longer available.")
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
                            "slot": current_creator["preferred_slot"],
                            "deal": cafe["deal_type"],
                            "confirmed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "status": "Confirmed & Locked on Collabé 🔒"
                        }
                        st.session_state.bookings.append(booking_record)
                        save_data(BOOKINGS_FILE, st.session_state.bookings)
                        st.toast(f"Slot Locked on Collabé for {current_creator['name']} at {cafe['name']}!", icon="🎉")
                        st.rerun()
                        
                # WhatsApp dispatch link
                msg_text, wa_url = generate_whatsapp_message(current_creator, cafe, current_creator['preferred_slot'])
                col_btn2.link_button("📲 Send WhatsApp Alert", wa_url)
                
                with col_btn3.expander("Preview WhatsApp Notification"):
                    st.code(msg_text, language="text")

            # CASE B: SLOT BOOKED
            elif status == "SLOT_TAKEN":
                has_any_match = True
                booked_by = [b for b in st.session_state.bookings if b.get("cafe_id") == cafe["id"] and b.get("slot") == current_creator["preferred_slot"]]
                my_booking = next((b for b in booked_by if b.get("creator_id") == current_creator["id"]), None)
                
                # B.1: THIS CREATOR THEMSELVES BOOKED THIS SLOT!
                if my_booking:
                    st.balloons()
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 12px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h2 style="margin: 0; color: white;">🎟️ Shoot Booking Confirmed & Locked!</h2>
                            <span style="background: white; color: #065f46; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">
                                Pass ID: {my_booking['booking_id']}
                            </span>
                        </div>
                        <p style="font-size: 1.1rem; margin-top: 10px; margin-bottom: 5px;">
                            <b>Venue:</b> {cafe['name']} ({cafe['sector']}) &nbsp;|&nbsp; 
                            <b>Slot:</b> {my_booking['slot']} &nbsp;|&nbsp; 
                            <b>Deal:</b> {cafe['deal_type']}
                        </p>
                        <p style="margin: 0; font-size: 0.95rem; opacity: 0.95;">
                            👤 <b>Creator:</b> {current_creator['name']} ({current_creator['handle']}) &nbsp;|&nbsp; 
                            📞 <b>Manager Contact:</b> +{cafe['manager_phone']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons for confirmed booking
                    col_act1, col_act2, col_act3 = st.columns([1.5, 1.5, 1])
                    
                    # 1. WhatsApp to Cafe Manager
                    mgr_msg = (
                        f"Hello {cafe['name']} Management! 🎬 (via Collabé)\n\n"
                        f"Great news! Creator {current_creator['name']} ({current_creator['handle']}, {current_creator['followers']} followers) has confirmed and locked the shoot slot on Collabé!\n\n"
                        f"🎟️ Booking ID: {my_booking['booking_id']}\n"
                        f"🕒 Slot: {my_booking['slot']}\n"
                        f"👥 Crew Size: {current_creator['crew_size']} people\n"
                        f"📸 Shoot: {current_creator['shoot_type']}\n"
                        f"💡 Agreed Deal: {cafe['deal_type']}\n\n"
                        f"Please ensure a designated table is ready for the creator."
                    )
                    mgr_url = f"https://wa.me/{cafe['manager_phone']}?text={urllib.parse.quote(mgr_msg)}"
                    col_act1.link_button("📲 Notify Café Manager on WhatsApp", mgr_url)
                    
                    # 2. WhatsApp pass to Creator
                    pass_msg = (
                        f"🎉 Collabé Official Shoot Pass!\n\n"
                        f"Booking ID: {my_booking['booking_id']}\n"
                        f"Creator: {current_creator['name']} ({current_creator['handle']})\n"
                        f"Venue: {cafe['name']}, {cafe['sector']}\n"
                        f"Slot: {my_booking['slot']}\n"
                        f"Deal: {cafe['deal_type']}\n\n"
                        f"Please show this pass upon arrival at the café."
                    )
                    pass_url = f"https://wa.me/{current_creator['whatsapp']}?text={urllib.parse.quote(pass_msg)}"
                    col_act2.link_button("📲 Send Pass to Creator WhatsApp", pass_url)
                    
                    # 3. Cancel / Release Slot Button (for testing)
                    if col_act3.button("❌ Release Slot", key=f"cancel_{my_booking['booking_id']}"):
                        st.session_state.bookings = [b for b in st.session_state.bookings if b["booking_id"] != my_booking["booking_id"]]
                        save_data(BOOKINGS_FILE, st.session_state.bookings)
                        st.toast("Booking cancelled. Slot has been reopened!", icon="🔄")
                        st.rerun()

                # B.2: BOOKED BY ANOTHER CREATOR
                else:
                    other_creator_name = booked_by[0]['creator_name'] if booked_by else "another creator"
                    st.markdown(f"""
                    <div class="slot-taken-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #9b1c1c;">🔴 {cafe['name']} — {cafe['sector']}</h3>
                            <span class="badge-danger">Slot Already Booked by {other_creator_name}</span>
                        </div>
                        <p style="margin-top: 8px; margin-bottom: 5px; color: #771d1d;">
                            <b>Requested Slot:</b> <code>{current_creator['preferred_slot']}</code> is <b>UNAVAILABLE ❌</b> because {other_creator_name} accepted and locked it first.
                        </p>
                        <p style="margin-bottom: 0px;">
                            <b>Good News:</b> This café still has other open slots: <b>{', '.join(remaining_slots) if remaining_slots else 'None left'}</b>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if remaining_slots:
                        st.markdown("**👉 Book an alternative available slot at this café instead:**")
                        col_alt1, col_alt2 = st.columns([2, 1])
                        alt_slot = col_alt1.selectbox(f"Choose other open slot at {cafe['name']}:", remaining_slots, key=f"alt_select_{cafe['id']}")
                        if col_alt2.button(f"Book '{alt_slot}'", key=f"btn_alt_{cafe['id']}"):
                            booking_record = {
                                "booking_id": f"CLB_{datetime.now().strftime('%m%d_%H%M%S')}",
                                "creator_id": current_creator["id"],
                                "creator_name": current_creator["name"],
                                "creator_handle": current_creator["handle"],
                                "creator_phone": current_creator["whatsapp"],
                                "cafe_id": cafe["id"],
                                "cafe_name": cafe["name"],
                                "sector": cafe["sector"],
                                "slot": alt_slot,
                                "deal": cafe["deal_type"],
                                "confirmed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "status": "Confirmed & Locked on Collabé 🔒"
                            }
                            st.session_state.bookings.append(booking_record)
                            save_data(BOOKINGS_FILE, st.session_state.bookings)
                            st.toast(f"Booked alternate slot '{alt_slot}' at {cafe['name']} on Collabé!", icon="🎉")
                            st.rerun()

        if not has_any_match:
            st.markdown("""
            <div class="no-match-card">
                <h3 style="color: #856404; margin-top: 0;">⚠️ No Available Match for This Creator</h3>
                <p>None of the registered cafés meet the creator's rules (crew size, equipment, or slot availability).</p>
            </div>
            """, unsafe_allow_html=True)

# ----------------- PAGE 2: CREATOR FORM -----------------
elif page == "📝 Creator / Brand Request Form":
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Creator & Small Brand Shoot Brief Registration</div>', unsafe_allow_html=True)
    
    with st.form("creator_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Creator / Brand Name *", placeholder="e.g. Aarav Mehra")
        handle = col2.text_input("Instagram Handle *", placeholder="e.g. @aarav_shoots")
        
        col3, col4 = st.columns(2)
        followers = col3.selectbox("Follower Range *", ["Under 1K", "1K – 5K", "5K – 10K", "10K – 50K", "50K+"])
        whatsapp = col4.text_input("WhatsApp Phone (with Country Code) *", value="917814259209", placeholder="917814259209")
        
        st.markdown("---")
        shoot_type = st.selectbox(
            "What are you creating? *", 
            ["Fashion & Lifestyle", "Food & Beverage", "UGC / Brand Content", "Product Shoot", "Music / Commercial", "Other"]
        )
        description = st.text_area("Describe the shoot in one or two lines *", placeholder="e.g. Seasonal fashion lookbook shoot with 1 model")
        
        col5, col6, col7 = st.columns(3)
        preferred_sector = col5.selectbox("Preferred Location / Sector", ["Sector 9", "Sector 8", "Sector 7", "Sector 26", "Sector 35"])
        preferred_slot = col6.selectbox("Preferred Time Window *", [
            "Morning (8 AM - 11 AM)", 
            "Morning (8 AM - 10 AM)", 
            "Morning (10 AM - 1 PM)", 
            "Afternoon (3 PM - 5 PM)", 
            "Afternoon (2 PM - 5 PM)", 
            "Evening (5 PM - 7 PM)"
        ])
        crew_size = col7.number_input("How many people on set? (Crew size) *", min_value=1, max_value=10, value=3)
        
        col8, col9 = st.columns(2)
        needs_tripod = col8.checkbox("Tripod / Lighting Gear Required?", value=True)
        needs_natural_light = col9.checkbox("High Natural Window Light Required?", value=True)
        
        budget_pref = st.selectbox("Compensation / Deal Preference", [
            "Free in exchange for 1 tagged Reel", 
            "Free coffee & meal with tag", 
            "Minimum spend ₹500", 
            "Hourly fee ₹800/hr"
        ])
        
        submitted = st.form_submit_button("🚀 Submit Shoot Brief to Collabé")
        if submitted:
            if not name or not handle or not whatsapp or not description:
                st.error("Please fill all required fields (*).")
            else:
                new_creator = {
                    "id": f"creator_{len(st.session_state.creators)+1}",
                    "name": name,
                    "handle": handle,
                    "followers": followers,
                    "whatsapp": whatsapp,
                    "shoot_type": shoot_type,
                    "description": description,
                    "preferred_sector": preferred_sector,
                    "preferred_slot": preferred_slot,
                    "crew_size": crew_size,
                    "needs_tripod": needs_tripod,
                    "needs_natural_light": needs_natural_light,
                    "budget_pref": budget_pref,
                    "status": "Pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.creators.append(new_creator)
                save_data(CREATORS_FILE, st.session_state.creators)
                st.success("🎉 Shoot brief submitted to Collabé! Go to '⚡ Live Matching' to test.")

# ----------------- PAGE 3: CAFÉ FORM -----------------
elif page == "☕ Café & Venue Setup":
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Café & Restaurant Venue Registration</div>', unsafe_allow_html=True)
    
    with st.form("cafe_form"):
        col1, col2 = st.columns(2)
        cafe_name = col1.text_input("Café / Venue Name *", placeholder="e.g. The Willow Café")
        sector = col2.selectbox("Location / Sector *", ["Sector 7", "Sector 8", "Sector 9", "Sector 26", "Sector 35"])
        
        col3, col4 = st.columns(2)
        manager_phone = col3.text_input("Manager WhatsApp Phone *", value="917814259209", placeholder="917814259209")
        max_crew = col4.number_input("Maximum Crew Permitted *", min_value=1, max_value=15, value=4)
        
        slots = st.multiselect(
            "Select all quiet slots available for shoots *",
            [
                "Morning (8 AM - 10 AM)", 
                "Morning (8 AM - 11 AM)", 
                "Morning (10 AM - 1 PM)", 
                "Afternoon (2 PM - 5 PM)", 
                "Afternoon (3 PM - 5 PM)", 
                "Evening (5 PM - 7 PM)"
            ],
            default=["Morning (8 AM - 11 AM)", "Afternoon (3 PM - 5 PM)"]
        )
        
        col5, col6 = st.columns(2)
        allows_tripod = col5.checkbox("Allow Tripods & Ring Lights?", value=True)
        has_natural_light = col6.checkbox("Ample Natural Window Light?", value=True)
        
        deal_type = st.selectbox(
            "Deal Model Offered to Creators",
            [
                "Free in exchange for 1 tagged Reel", 
                "Free coffee & meal with tag", 
                "Minimum spend ₹500", 
                "Hourly fee ₹800/hr"
            ]
        )
        
        if st.form_submit_button("🏪 Register Café on Collabé"):
            if not cafe_name or not manager_phone or not slots:
                st.error("Please fill all required venue details.")
            else:
                new_cafe = {
                    "id": f"cafe_{len(st.session_state.cafes)+1}",
                    "name": cafe_name,
                    "sector": sector,
                    "slots": slots,
                    "max_crew": max_crew,
                    "allows_tripod": allows_tripod,
                    "has_natural_light": has_natural_light,
                    "allowed_shoots": ["Food & Beverage", "Fashion & Lifestyle", "UGC / Brand Content"],
                    "deal_type": deal_type,
                    "manager_phone": manager_phone
                }
                st.session_state.cafes.append(new_cafe)
                save_data(CAFES_FILE, st.session_state.cafes)
                st.success(f"🎉 {cafe_name} added to Collabé!")

# ----------------- PAGE 4: TABULAR DATA & BOOKINGS -----------------
elif page == "📊 Live Tabular Data & Slot Status":
    st.markdown('<div class="brand-header">Collabé</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live Tabular Data & Real-Time Slot Status</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤝 Confirmed Bookings", "☕ Cafés & Slot Inventory", "📝 Creator Briefs"])
    
    with tab1:
        st.markdown(f"**Total Confirmed Bookings on Collabé:** {len(st.session_state.bookings)}")
        if st.session_state.bookings:
            df_b = pd.DataFrame(st.session_state.bookings)
            st.dataframe(df_b, width='stretch')
        else:
            st.info("No bookings yet. Accept a booking on the Live Matching page to see it recorded here.")
            
    with tab2:
        st.markdown("**Real-Time Slot Availability per Café:**")
        cafe_status_list = []
        booked_map = get_booked_slots()
        for c in st.session_state.cafes:
            b_slots = list(booked_map.get(c["id"], []))
            avail_slots = [s for s in c["slots"] if s not in b_slots]
            cafe_status_list.append({
                "Café Name": c["name"],
                "Sector": c["sector"],
                "All Slots": ", ".join(c["slots"]),
                "Booked / Locked Slots": ", ".join(b_slots) if b_slots else "None (All Open)",
                "Available Open Slots": ", ".join(avail_slots) if avail_slots else "Fully Booked ❌",
                "Max Crew": c["max_crew"],
                "Tripods Allowed": "Yes" if c["allows_tripod"] else "No"
            })
        st.dataframe(pd.DataFrame(cafe_status_list), width='stretch')
        
    with tab3:
        st.dataframe(pd.DataFrame(st.session_state.creators), width='stretch')
