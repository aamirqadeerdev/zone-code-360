
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ZoneCode 360", layout="wide")

def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    def password_entered():
        if st.session_state["password"] == st.secrets["client_access"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else: st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.sidebar.text_input("Consultant Login", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password(): st.stop()

st.title("ZoneCode 360 Dashboard")
with st.form("query_form"):
    address = st.text_input("Enter Property Address")
    project_type = st.selectbox("Project Type", ["Fence Installation", "Interior Remodel", "Roof Replacement"])
    submitted = st.form_submit_button("Generate Game Plan", type="primary")

if submitted and address:
    try:
        genai.configure(api_key=st.secrets["api_keys"]["gemini"])
        
        # This automatically finds the right model for your specific API key!
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else valid_models[0]
        
        with st.spinner("AI is analyzing local municipal codes..."):
            model = genai.GenerativeModel(best_model)
            prompt = f"Act as a Senior US Zoning Expediter. Address: {address}. Project: {project_type}. Provide a professional Permit Game Plan including constraints, setbacks, red flags, and forms. No emojis."
            response = model.generate_content(prompt)
            st.markdown("### Official Permit Game Plan")
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error: {e}")
