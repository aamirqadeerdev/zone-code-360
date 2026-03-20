
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
    
    /* Clean Document Card for the AI Report */
    .main-card {
        background-color: #ffffff; border-radius: 12px; padding: 2.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    /* Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px; border: 1px solid #cbd5e1; background-color: #ffffff;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border: 2px solid #2563eb !important; box-shadow: none;
    }
    
    /* Professional Blue Buttons (Applies to both Submit and Download) */
    .stButton>button, .stDownloadButton>button {
        background-color: #2563eb !important; color: white !important;
        border-radius: 8px !important; border: none !important;
        padding: 0.6rem 1.5rem !important; font-weight: 600 !important; width: 100%;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stDownloadButton>button:hover { 
        background-color: #1d4ed8 !important; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
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
        st.sidebar.markdown("### Secure Login")
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
    st.markdown("<p style='margin-bottom: 2.5rem;'>Instantly generate Permit Game Plans and check Zoning regulations.</p>", unsafe_allow_html=True)

    # Removed the white rectangle wrapper here for a cleaner look!
    st.markdown("### Project Details")
    
    # Removed emojis from inputs for strict professional look
    address = st.text_input("Property Address", placeholder="e.g., 6410 I-45, La Marque, TX 77568")
    
    main_category = st.selectbox("Building Type", list(PROJECT_CATEGORIES.keys()))
    sub_category = st.selectbox("Specific Project", PROJECT_CATEGORIES[main_category])
    
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.button("Generate Permit Game Plan", type="primary")

# --- 5. PROCESSING WITH AI & GOOGLE MAPS ---
if submitted and address:
    st.markdown("---") 
    
    # --- GOOGLE MAPS EMBED (FULL WIDTH) ---
    gmaps_key = st.secrets["api_keys"].get("google_maps", "YOUR_GOOGLE_MAPS_KEY_HERE")
    
    if gmaps_key == "YOUR_GOOGLE_MAPS_KEY_HERE" or not gmaps_key:
        st.warning("Google Maps API Key is missing from secrets. Map cannot load.")
    else:
        address_encoded = urllib.parse.quote(address)
        map_url = f"https://www.google.com/maps/embed/v1/place?key={gmaps_key}&q={address_encoded}"
        st.components.v1.iframe(map_url, width=100, height=250, scrolling=False)
        st.markdown("""<style>iframe { width: 100% !important; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;}</style>""", unsafe_allow_html=True)

    # --- AI GENERATION & DOWNLOAD BUTTON ---
    try:
        genai.configure(api_key=st.secrets["api_keys"]["gemini"])
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else valid_models[0]
        
        with st.spinner("Analyzing local municipal codes and building checklist..."):
            model = genai.GenerativeModel(best_model)
            
            prompt = f"""
            Act as a Senior US Zoning Expediter. Address: {address}. Building Type: {main_category}. Project Scope: {sub_category}. 
            First, provide a professional Permit Game Plan including constraints, setbacks, red flags, and forms.
            Second, at the very end of the report, add a section titled "### Action Checklist". This checklist MUST be written in simple, Grade 7 English. Use short, numbered sentences telling the contractor exactly what physical steps to take next (e.g., "1. Call the city to ask about...").
            Do NOT use emojis anywhere in the response.
            """
            
            response = model.generate_content(prompt)
            report_text = response.text
            
            st.success(f"Analysis & Checklist Complete for: {address}")
            
            # Professional Download Button (No emoji, solid blue)
            st.download_button(
                label="Download Game Plan & Checklist",
                data=report_text,
                file_name="Permit_Game_Plan.txt",
                mime="text/plain",
                type="primary"
            )
            
            # The Checklist and Report displayed beautifully on the website
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown(report_text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("Disclaimer: This AI tool provides preliminary zoning guidance. Always verify with the local AHJ.")
            
    except Exception as e:
        st.error(f"Error connecting to AI: {e}")
