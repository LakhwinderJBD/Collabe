# 🎬 Collabé
### *The Creator & Café Match Network*

> **Collabé** connects content creators and small lifestyle brands with aesthetic cafés and restaurants in Chandigarh for hourly shoot bookings during their dead hours.

---

## 🌟 Key Features

1. **📝 Creator & Brand Shoot Brief Form**
   - Submit shoot requirements once (niche, crew size, equipment, preferred quiet slots, deal model).
   - Instant compatibility evaluation against verified Chandigarh venues.

2. **☕ Café & Venue Setup**
   - List quiet dead-hour slots (e.g., Morning 8–11 AM, Afternoon 3–5 PM).
   - Set max crew limits, tripod/lighting permissions, and promotional deal terms (e.g. Free with tagged reel, minimum spend, or hourly rental).

3. **⚡ Real-Time Slot Locking & Race-Condition Prevention**
   - If two creators request the same slot at the same venue, the first to accept locks it.
   - The second creator is automatically notified that the slot was taken and presented with alternative open slots at that café.

4. **📲 One-Click WhatsApp Dispatch**
   - Pre-formatted, personalized messages for both the Creator and the Café Manager.
   - Generates clickable `https://wa.me/...` links with shoot passes, booking IDs, and confirmed details.

5. **📊 Live Tabular Data View**
   - Inspect raw database tables: registered venues, creator requests, and confirmed bookings with timestamps.

---

## 📁 Repository Structure

```text
├── app.py              # Main Streamlit matching application & UI
├── requirements.txt    # Python dependencies for deployment
├── README.md           # Project documentation & setup instructions
└── data/               # Persistent JSON database
    ├── cafes.json      # Registered Chandigarh café inventory & rules
    ├── creators.json   # Submitted creator & brand shoot briefs
    └── bookings.json   # Real-time confirmed & locked bookings
```

---

## 🚀 How to Run Locally

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Collabé application:
   ```bash
   streamlit run app.py
   ```
4. Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying to Streamlit Community Cloud (Free)

1. Upload this repository to your **GitHub** account.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **"New app"** and select this repository.
4. Set the main file path to `app.py`.
5. Click **Deploy** — your app is now live with a permanent public URL accessible worldwide!

---

*Developed for Startup Market Lab — Collabé Pilot (Chandigarh)*
