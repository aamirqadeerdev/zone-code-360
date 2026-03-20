
import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="ZoneCode 360", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f4f7f9; }
    h1, h2, h3 { color: #1e3a8a !important; font-weight: 700 !important; }
    p, label { color: #475569 !important; font-weight: 600 !important; }
    .main-card {
        background-color: #ffffff; border-radius: 16px; padding: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px; border: 1px solid #cbd5e1; background-color: #f8fafc;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border: 2px solid #2563eb !important; box-shadow: none;
    }
    .stButton>button {
        background-color: #2563eb !important; color: white !important;
        border-radius: 8px !important; border: none !important;
        padding: 0.6rem 1.5rem !important; font-weight: 600 !important; width: 100%;
    }
    .stButton>button:hover { background-color: #1d4ed8 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. SECURE CLIENT ACCESS GATE ---
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    def password_entered():
        if st.session_state["password"] == st.secrets["client_access"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else: st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.sidebar.markdown("### 🔒 Secure Login")
        st.sidebar.text_input("Consultant Access Code", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.markdown("<br><br><br><h1 style='text-align: center;'>ZoneCode 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Enterprise Permit & Zoning Navigator. Please log in via the sidebar.</p>", unsafe_allow_html=True)
    st.stop()

# --- 3. CATEGORY DICTIONARY ---
PROJECT_CATEGORIES = {
    "Residential Building": ["Single-Family Home", "Townhouse", "Multi-Family (Apartments)", "ADU (Accessory Dwelling)", "Interior Remodel", "Fence / Deck"],
    "Commercial Building": ["Retail Space / Storefront", "Office Remodel", "Restaurant / Cafe", "Mixed-Use Development"],
    "Industrial Building": ["Warehouse / Storage", "Manufacturing Facility", "Distribution Center"]
}

# --- 4. THE MAIN DASHBOARD ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h1>ZoneCode 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 2rem;'>Instantly generate Permit Game Plans and check Zoning regulations.</p>", unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### Project Details")
    
    address = st.text_input("📍 Property Address", placeholder="e.g., 6410 I-45, La Marque, TX 77568")
    
    # Dynamic Dropdowns
    main_category = st.selectbox("🏢 Building Type", list(PROJECT_CATEGORIES.keys()))
    sub_category = st.selectbox("🛠️ Specific Project", PROJECT_CATEGORIES[main_category])
    
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.button("Generate Permit Game Plan", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. PROCESSING WITH AI & GOOGLE MAPS ---
if submitted and address:
    with col2:
        # --- GOOGLE MAPS EMBED ---
        st.markdown("### 🗺️ Project Location")
        gmaps_key = st.secrets["api_keys"].get("google_maps", "YOUR_GOOGLE_MAPS_KEY_HERE")
        
        if gmaps_key == "YOUR_GOOGLE_MAPS_KEY_HERE" or not gmaps_key:
            st.warning("⚠️ Google Maps API Key is missing from secrets. Map cannot load.")
        else:
            address_encoded = urllib.parse.quote(address)
            map_url = f"https://www.google.com/maps/embed/v1/place?key={gmaps_key}&q={address_encoded}"
            st.components.v1.iframe(map_url, width=100, height=400, scrolling=False)
            # Make iframe responsive using CSS injection hack for Streamlit components
            st.markdown("""<style>iframe { width: 100% !important; border-radius: 12px; border: 1px solid #cbd5e1; }</style>""", unsafe_allow_html=True)

        # --- AI GENERATION ---
        try:
            genai.configure(api_key=st.secrets["api_keys"]["gemini"])
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            best_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else valid_models[0]
            
            with st.spinner("Analyzing local municipal codes..."):
                model = genai.GenerativeModel(best_model)
                prompt = f"Act as a Senior US Zoning Expediter. Address: {address}. Building Type: {main_category}. Project Scope: {sub_category}. Provide a professional Permit Game Plan including constraints, setbacks, red flags, and forms. No emojis."
                response = model.generate_content(prompt)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.success(f"Analysis Complete for: {address}")
                st.markdown('<div class="main-card">', unsafe_allow_html=True)
                st.markdown("### 📋 Official Permit Game Plan")
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                st.info("Disclaimer: This AI tool provides preliminary zoning guidance. Always verify with the local AHJ.")
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")
