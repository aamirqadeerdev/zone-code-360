
import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="ZoneCode 360", layout="wide")

# Injecting CivicAtlas-style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Font and Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #f4f7f9; /* Soft light gray/blue background */
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #1e3a8a !important; /* Deep Navy Blue */
        font-weight: 700 !important;
    }
    p, label {
        color: #475569 !important; /* Slate gray for readable text */
    }

    /* The Main Form Container (The "Card") */
    [data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #e2e8f0;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        background-color: #f8fafc;
        transition: border 0.3s;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border: 2px solid #2563eb !important; /* Bright blue focus */
        box-shadow: none;
    }

    /* Primary Submit Button */
    .stButton>button {
        background-color: #2563eb !important; /* CivicAtlas bright blue */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important; /* Darker blue on hover */
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px);
    }

    /* Alert Boxes (Success/Info) */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
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
        st.sidebar.markdown("### 🔒 Secure Login")
        st.sidebar.text_input("Consultant Access Code", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.markdown("<br><br><br><h1 style='text-align: center;'>ZoneCode 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Enterprise Permit & Zoning Navigator. Please log in via the sidebar.</p>", unsafe_allow_html=True)
    st.stop()

# --- 3. THE MAIN DASHBOARD & QUERY FORM ---
# Use columns to center the card on large screens
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h1>ZoneCode 360</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 2rem;'>Instantly generate Permit Game Plans and check Zoning regulations.</p>", unsafe_allow_html=True)

    with st.form("query_form"):
        st.markdown("### Project Details")
        address = st.text_input("Property Address", placeholder="e.g., 6410 I-45, La Marque, TX 77568")
        project_type = st.selectbox("Project Type", ["Interior Remodel", "New Townhouse / Multi-Family", "Fence Installation", "Roof Replacement", "Mixed-Use Zoning"])
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate Game Plan", type="primary")

# --- 4. PROCESSING THE REQUEST WITH AI ---
if submitted and address:
    with col2:
        try:
            genai.configure(api_key=st.secrets["api_keys"]["gemini"])
            
            valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            best_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else valid_models[0]
            
            with st.spinner("Analyzing local municipal codes..."):
                model = genai.GenerativeModel(best_model)
                prompt = f"Act as a Senior US Zoning Expediter. Address: {address}. Project: {project_type}. Provide a professional Permit Game Plan including constraints, setbacks, red flags, and forms. No emojis."
                response = model.generate_content(prompt)
                
                st.success(f"Analysis Complete for: {address}")
                st.markdown("---")
                st.markdown("### Official Permit Game Plan")
                st.markdown(response.text)
                st.info("Disclaimer: This AI tool provides preliminary zoning guidance. Always verify with the local AHJ.")
        except Exception as e:
            st.error(f"Error: {e}")

