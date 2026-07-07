# ui/styles.py
import streamlit as st

def inject_premium_saas_styles() -> None:
    """
    Installs the heavens.pro inspired 2026 SaaS visual system.
    Strictly decoupled from UI rendering logic.
    """
    st.markdown(
        """
        <style>
        /* Design Tokens */
        :root {
            --bg-base: #050505;
            --bg-surface: rgba(15, 15, 17, 0.55);
            --border-glow: rgba(0, 245, 212, 0.25);
            --border-subtle: rgba(255, 255, 255, 0.06);
            --text-primary: #FAFAFA;
            --text-secondary: #A1A1AA;
            --accent-teal: #00F5D4;
            --accent-purple: #8B5CF6;
            --radius-lg: 12px;
            --radius-md: 8px;
            --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Deep space background with dual auroras */
        .stApp {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 10% 0%, rgba(0, 245, 212, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 100%, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
            color: var(--text-primary);
        }

        /* Eliminate Streamlit's default top padding for a true app feel */
        .block-container {
            padding-top: 2rem !important;
            max-width: 1400px;
        }

        /* Universal Glassmorphism Surface Pattern */
        .glass-card, div[data-testid="stMetric"], .stDataFrame {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(24px) saturate(160%);
            -webkit-backdrop-filter: blur(24px) saturate(160%);
            box-shadow: var(--shadow-glass);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        /* Executive Micro-interactions */
        .glass-card:hover {
            border-color: var(--border-glow);
            transform: translateY(-2px);
        }

        /* Typography Polish */
        h1, h2, h3 { 
            letter-spacing: -0.03em; 
            font-weight: 600; 
            color: var(--text-primary);
        }
        
        .section-kicker { 
            color: var(--accent-teal); 
            letter-spacing: 0.12em; 
            font-size: 0.75rem; 
            text-transform: uppercase; 
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        /* Premium Buttons */
        .stButton > button {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--text-secondary);
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-teal) 0%, #14B8A6 100%);
            color: #000;
            border: none;
            box-shadow: 0 0 20px rgba(0, 245, 212, 0.15);
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True
    )