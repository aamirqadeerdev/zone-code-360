

import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
# Removed the emoji icon. It will now default to a clean, standard browser tab.
st.set_page_config(page_title="ZoneCode 360 | Pro Permit Navigator", layout="wide")

# --- 2. SECURE CLIENT ACCESS GATE ---
def check_password():
    """
    Returns `True` if the user has entered the correct password from secrets.toml.
    """
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    def password_entered():
        if st.session_state["password"] == st.secrets["client_access"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.sidebar.markdown("### Consultant Login")
        st.sidebar.text_input(
            "Enter Access Code", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Contact your ZoneCode 360 representative for trial access."
        )
        return False
    
    return True

# If the password is wrong or missing, stop the app completely here.
if not check_password():
    st.title("Welcome to ZoneCode 360")
    st.markdown("### The AI-Powered Permit & Zoning Navigator for US Contractors.")
    st.info("Authentication Required: Please enter your Consultant Access Code in the left sidebar to unlock the application.")
    st.stop()

# --- 3. THE MAIN DASHBOARD & QUERY FORM ---
st.title("ZoneCode 360 Dashboard")
st.markdown("### Instantly generate Permit Game Plans and check Zoning regulations.")

with st.container():
    st.markdown("#### Step 1: Project Details")
    
    with st.form("project_query_form"):
        # Address Input
        address = st.text_input(
            "Enter Property Address", 
            placeholder="e.g., 123 Main St, Austin, TX 78701"
        )
        
        # Project Type Dropdown
        project_type = st.selectbox(
            "Select Project Type", 
            [
                "Fence Installation", 
                "Deck / Patio Addition", 
                "ADU (Accessory Dwelling Unit)", 
                "Interior Remodel",
                "Roof Replacement"
            ]
        )
        
        # Submit Button
        submitted = st.form_submit_button("Generate Permit Game Plan", type="primary")

# --- 4. PROCESSING THE REQUEST WITH AI ---
if submitted:
    if not address:
        st.error("Input Error: Please enter a valid US property address to continue.")
    else:
        st.success(f"Locating address: {address}...")
        
        try:
            GEMINI_API_KEY = st.secrets["api_keys"]["gemini"]
            genai.configure(api_key=GEMINI_API_KEY)
        except KeyError:
            st.error("System Error: API Key Missing. Please add your Gemini API key to .streamlit/secrets.toml.")
            st.stop()
        
        with st.spinner("AI Zoning Consultant is analyzing local municipal codes..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                # Notice the added instruction: "Do NOT use emojis."
                system_prompt = f"""
                Act as a Senior US Building Code Official and Zoning Expediter with 20 years of experience.
                The contractor is working at this exact address: {address}.
                Project Type: {project_type}.
                
                Provide a highly professional "Permit Game Plan" including:
                1. Likely Zoning district and constraints for this specific city.
                2. Standard Setbacks (Explicitly remind them to measure from the legally surveyed Property Line, not the street curb).
                3. "Red Flag" Warnings: Tell them they must check for Historic Districts, Utility Easements, Wetland, or FEMA flood zones.
                4. Required Permit Forms typically needed for this project type in this jurisdiction.
                
                Format the output beautifully using Markdown (bullet points, bold text). 
                Do NOT use emojis. Keep the tone strictly professional, authoritative, corporate, and actionable for a US contractor.
                """
                
                response = model.generate_content(system_prompt)
                
                st.markdown("---")
                st.markdown("### Official Permit Game Plan")
                st.markdown(response.text)
                
                st.info("Disclaimer: This AI tool provides preliminary zoning guidance. Always verify with the local AHJ (Authority Having Jurisdiction) before breaking ground.")
                
            except Exception as e:
                st.error(f"Application Error: An error occurred while contacting the AI server: {e}")

