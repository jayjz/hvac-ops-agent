# ui/styles.py
import streamlit as st

def inject_premium_saas_styles() -> None:
    """
    Installs the heavens.pro inspired 2026 SaaS visual system.
    Aggressively overrides Streamlit's native DOM elements using data-testids.
    """
    st.markdown(
        """
        <style>
        /* 1. Base Design Tokens (Heavens.pro DNA) */
        :root {
            --bg-base: #050505;
            --bg-surface: rgba(15, 15, 17, 0.45);
            --bg-glass: rgba(20, 20, 25, 0.65);
            --border-glow: rgba(0, 245, 212, 0.35);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --text-primary: #FAFAFA;
            --text-secondary: #A1A1AA;
            --accent-teal: #00F5D4;
            --accent-purple: #8B5CF6;
            --radius-lg: 16px;
            --radius-md: 12px;
            --shadow-glass: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        }

        /* 2. Global App Shell, Noise Textures & Auroras */
        .stApp {
            background-color: var(--bg-base) !important;
            background-image: 
                radial-gradient(circle at 15% 0%, rgba(0, 245, 212, 0.07) 0%, transparent 45%),
                radial-gradient(circle at 85% 100%, rgba(139, 92, 246, 0.07) 0%, transparent 45%),
                url('data:image/svg+xml;utf8,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)" opacity="0.04"/%3E%3C/svg%3E') !important;
            color: var(--text-primary);
        }

        /* Clean up standard Streamlit chrome */
        .block-container {
            padding-top: 2.5rem !important;
            max-width: 1440px !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Typography & Tracking (-0.03em) */
        h1, h2, h3, h4, h5, h6, span, p, div {
            letter-spacing: -0.03em !important;
        }
        h1, h2, h3 { 
            font-weight: 700 !important; 
        }

        /* 3. Aggressive Native Component Overrides */

        /* Native Dataframes & Tables */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            backdrop-filter: blur(20px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
            box-shadow: var(--shadow-glass) !important;
            overflow: hidden !important;
        }
        
        th {
            background: rgba(255, 255, 255, 0.02) !important;
            color: var(--accent-teal) !important;
            border-bottom: 1px solid var(--border-subtle) !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em !important;
            font-size: 0.75rem !important;
        }

        td {
            color: var(--text-primary) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        }

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(10, 10, 12, 0.65) !important;
            border-right: 1px solid var(--border-subtle) !important;
            backdrop-filter: blur(24px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
        }

        /* Native Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 1px solid var(--border-subtle) !important;
            gap: 1.5rem !important;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            border: none !important;
            padding-bottom: 0.75rem !important;
            transition: color 0.2s ease !important;
        }

        .stTabs [aria-selected="true"] {
            color: var(--accent-teal) !important;
            border-bottom: 2px solid var(--accent-teal) !important;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: var(--bg-surface) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            backdrop-filter: blur(20px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
            padding: 1.25rem !important;
            box-shadow: var(--shadow-glass) !important;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            border-color: var(--border-glow) !important;
            transform: translateY(-2px);
        }

        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            font-size: 2.2rem !important;
        }

        [data-testid="stMetricLabel"] {
            color: var(--accent-teal) !important;
            text-transform: uppercase;
            letter-spacing: 0.1em !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
        }

        /* Custom Glass Cards (For your markdown wrappers) */
        .glass-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(20px) saturate(150%);
            -webkit-backdrop-filter: blur(20px) saturate(150%);
            box-shadow: var(--shadow-glass);
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-card:hover {
            border-color: var(--border-glow);
            transform: translateY(-3px);
            box-shadow: 0 16px 50px -5px rgba(0, 245, 212, 0.2);
        }
        
        .section-kicker { 
            color: var(--accent-teal); 
            letter-spacing: 0.12em; 
            font-size: 0.75rem; 
            text-transform: uppercase; 
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        /* Form Inputs (Text Area, Toggles) */
        .stTextArea textarea {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid var(--border-subtle) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-md) !important;
        }
        
        .stTextArea textarea:focus {
            border-color: var(--accent-purple) !important;
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.3) !important;
        }

        /* Primary Button Enhancements */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-teal) 0%, #14B8A6 100%) !important;
            color: #050505 !important;
            border: none !important;
            box-shadow: 0 0 20px rgba(0, 245, 212, 0.25) !important;
            font-weight: 800 !important;
            border-radius: var(--radius-md) !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 0 30px rgba(0, 245, 212, 0.4) !important;
            transform: scale(1.02) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )