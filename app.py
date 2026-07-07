# app.py
import streamlit as st

# Core setup imports
from core.state_manager import initialize_app_state
from ui.styles import inject_premium_saas_styles

# View imports (You will create these in the next step)
from views.dispatch_workspace import render_dispatch_workspace
# from views.technician_view import render_technician_view
# from views.ar_operations import render_ar_operations

APP_TITLE = "HVAC OpsForge"

def main() -> None:
    # 1. Page Config must be the first Streamlit command
    st.set_page_config(
        page_title=f"{APP_TITLE} | Executive Board",
        page_icon="AF",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # 2. Initialize predictable state
    initialize_app_state()
    
    # 3. Inject visual system
    inject_premium_saas_styles()

    # 4. Global Navigation (Replaces horizontal tabs with enterprise sidebar routing)
    st.sidebar.markdown(
        '<div style="font-weight: 800; font-size: 1.2rem; color: #FAFAFA; margin-bottom: 2rem;">OpsForge</div>', 
        unsafe_allow_html=True
    )
    
    navigation = st.sidebar.radio(
        "Platform Modules",
        ["Dispatch Workspace", "Technician Field App", "Financial Ops (AR)"],
        label_visibility="collapsed"
    )

    st.sidebar.divider()
    
    # 5. Route to the correct view component
    if navigation == "Dispatch Workspace":
        render_dispatch_workspace()
    elif navigation == "Technician Field App":
        st.title("Field Mode")
        st.info("Migrate `render_technician_dispatch_tab()` logic here.")
        # render_technician_view()
    elif navigation == "Financial Ops (AR)":
        st.title("Accounts Receivable")
        st.info("Migrate `render_ar_tab()` logic here.")
        # render_ar_operations()

if __name__ == "__main__":
    main()