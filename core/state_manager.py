# core/state_manager.py
from typing import Any
import streamlit as st

def initialize_app_state() -> None:
    """
    Production-grade state initialization. 
    Guarantees all required session keys exist before any UI component renders,
    preventing KeyErrors during rapid tab switching or async callbacks.
    """
    default_state = {
        "live_mongo_enabled": False,
        "source_mode": "synthetic",
        "upload_dir": None,
        "upload_meta": {"count": 0, "size": 0, "names": []},
        "goals": [
            "Build an HVAC retrofit PM baseline.",
            "Identify procurement, controls, construction, and budget risks.",
            "Create an executive-ready schedule and action summary."
        ],
        "pm_result": None,
        "confirm_new_run": False,
        "confirm_reset": False,
    }

    for key, default_value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def clear_run_state() -> None:
    """Safely purges ephemeral run data without destroying global app config."""
    st.session_state.pop("pm_result", None)
    st.session_state.pop("ar_decision_feedback", None)
    
    # Clean up dynamically generated AR decision keys
    keys_to_delete = [k for k in st.session_state.keys() if str(k).startswith("ar_decision_")]
    for k in keys_to_delete:
        st.session_state.pop(k, None)