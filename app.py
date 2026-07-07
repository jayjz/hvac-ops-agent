# app.py
import streamlit as st
from ui_styles import inject_premium_saas_styles

# Future imports from your refactored views directory
# from views.dashboard import render_dashboard
# from views.technician import render_technician_tab

APP_TITLE = "HVAC OpsForge"

def main() -> None:
    st.set_page_config(page_title=f"{APP_TITLE}", page_icon="AF", layout="wide")
    
    # Inject the Heavens.pro styling engine
    inject_premium_saas_styles()

    st.sidebar.title("Navigation")
    view = st.sidebar.radio("Go to", ["Dispatch Baseline", "Technician Field View", "AR Queue"])

    if view == "Dispatch Baseline":
        st.title("Dispatch Workspace")
        st.info("Dashboard components go here.")
        # render_dashboard()
    elif view == "Technician Field View":
        st.title("Field Mode")
        st.info("Technician components go here.")
        # render_technician_tab()
    elif view == "AR Queue":
        st.title("Financial Operations")
        st.info("AR components go here.")

if __name__ == "__main__":
    main()