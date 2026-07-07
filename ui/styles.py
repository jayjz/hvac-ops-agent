"""
ui/styles.py

Global CSS injection for HVAC OpsForge — "Spatial Cyber-Physical" theme.
Inspired by heavens.pro/gallery: deep-space glassmorphism, floating elevation,
electric cyan/violet accent glow, cinematic typography.

Usage (in app.py, called once at the top of the router):
    from ui.styles import inject_global_css
    inject_global_css()
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens — single source of truth. Reuse these constants anywhere
# you need to match theme colors in matplotlib/Base64 chart generation
# (see ui/charts.py) so charts don't clash with the CSS theme.
# ---------------------------------------------------------------------------
TOKENS = {
    "bg_void": "#05070D",          # true black-slate base
    "bg_deep": "#0B0F1A",          # panel background
    "bg_panel": "rgba(18, 23, 38, 0.55)",   # glass panel fill
    "border_glass": "rgba(255, 255, 255, 0.08)",
    "border_glass_hover": "rgba(255, 255, 255, 0.16)",
    "accent_cyan": "#4CE6FF",
    "accent_violet": "#9D6BFF",
    "accent_cyan_glow": "rgba(76, 230, 255, 0.35)",
    "accent_violet_glow": "rgba(157, 107, 255, 0.35)",
    "text_primary": "#F4F6FB",
    "text_secondary": "#9AA4BF",
    "text_muted": "#5D6785",
    "success": "#3EE6A0",
    "warning": "#FFB84C",
    "danger": "#FF6B6B",
    "radius_lg": "20px",
    "radius_md": "14px",
    "radius_sm": "10px",
}


def inject_global_css() -> None:
    t = TOKENS
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --bg-void: {t['bg_void']};
            --bg-deep: {t['bg_deep']};
            --bg-panel: {t['bg_panel']};
            --border-glass: {t['border_glass']};
            --border-glass-hover: {t['border_glass_hover']};
            --accent-cyan: {t['accent_cyan']};
            --accent-violet: {t['accent_violet']};
            --glow-cyan: {t['accent_cyan_glow']};
            --glow-violet: {t['accent_violet_glow']};
            --text-primary: {t['text_primary']};
            --text-secondary: {t['text_secondary']};
            --text-muted: {t['text_muted']};
            --success: {t['success']};
            --warning: {t['warning']};
            --danger: {t['danger']};
            --radius-lg: {t['radius_lg']};
            --radius-md: {t['radius_md']};
            --radius-sm: {t['radius_sm']};
        }}

        /* ---------- Base canvas ---------- */
        .stApp {{
            background:
                radial-gradient(ellipse 1200px 600px at 15% -10%, rgba(157,107,255,0.14), transparent 60%),
                radial-gradient(ellipse 1000px 700px at 100% 10%, rgba(76,230,255,0.10), transparent 55%),
                var(--bg-void) !important;
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        h1, h2, h3, h4, .op-hero-title {{
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
        }}

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--bg-deep) 0%, var(--bg-void) 100%);
            border-right: 1px solid var(--border-glass);
        }}
        [data-testid="stSidebar"] * {{ color: var(--text-secondary); }}
        [data-testid="stSidebar"] .op-nav-item {{
            display: flex; align-items: center; gap: 10px;
            padding: 10px 14px; border-radius: var(--radius-sm);
            margin-bottom: 4px; transition: all 0.18s ease;
            border: 1px solid transparent; cursor: pointer;
        }}
        [data-testid="stSidebar"] .op-nav-item:hover {{
            background: var(--bg-panel);
            border-color: var(--border-glass);
        }}
        [data-testid="stSidebar"] .op-nav-item.active {{
            background: linear-gradient(90deg, var(--glow-cyan), transparent);
            border-color: var(--border-glass-hover);
            color: var(--text-primary);
        }}

        /* ---------- Buttons ---------- */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
            color: #05070D;
            border: none;
            border-radius: var(--radius-sm);
            font-weight: 600;
            padding: 0.5rem 1.2rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 0 0 rgba(76,230,255,0);
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 24px var(--glow-cyan);
        }}

        /* ---------- Metrics ---------- */
        [data-testid="stMetric"] {{
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 16px 18px;
        }}
        [data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; }}
        [data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-family: 'Space Grotesk'; }}

        /* ---------- Glass panel / card primitives (used by ui/components.py) ---------- */
        .op-glass {{
            background: var(--bg-panel);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}
        .op-glass:hover {{
            border-color: var(--border-glass-hover);
        }}
        .op-glass-elevated {{
            box-shadow: 0 12px 48px rgba(0,0,0,0.5), 0 0 40px var(--glow-violet);
        }}

        .op-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
            text-transform: uppercase; padding: 3px 10px; border-radius: 999px;
        }}
        .op-badge-success {{ background: rgba(62,230,160,0.14); color: var(--success); border: 1px solid rgba(62,230,160,0.3); }}
        .op-badge-warning {{ background: rgba(255,184,76,0.14); color: var(--warning); border: 1px solid rgba(255,184,76,0.3); }}
        .op-badge-danger  {{ background: rgba(255,107,107,0.14); color: var(--danger); border: 1px solid rgba(255,107,107,0.3); }}
        .op-badge-neutral {{ background: rgba(154,164,191,0.12); color: var(--text-secondary); border: 1px solid var(--border-glass); }}

        /* ---------- Fade-in animation for panels on render ---------- */
        @keyframes opFadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .op-glass, .op-hero {{ animation: opFadeIn 0.4s ease both; }}

        /* ---------- Hero header ---------- */
        .op-hero {{
            background: linear-gradient(135deg, rgba(157,107,255,0.12), rgba(76,230,255,0.08));
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 28px 32px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }}
        .op-hero::after {{
            content: '';
            position: absolute; inset: 0;
            background: radial-gradient(600px 200px at 90% 0%, var(--glow-cyan), transparent 70%);
            pointer-events: none;
        }}
        .op-hero-title {{ font-size: 1.8rem; font-weight: 700; margin: 0; }}
        .op-hero-sub {{ color: var(--text-secondary); margin-top: 4px; font-size: 0.95rem; }}

        /* ---------- Dataframes / tables ---------- */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            overflow: hidden;
        }}

        /* ---------- Scrollbar ---------- */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-void); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-glass-hover); border-radius: 8px; }}

        /* ---------- Hide default Streamlit chrome for a cleaner shell ---------- */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ background: transparent !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
