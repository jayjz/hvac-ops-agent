# ui/charts.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO

# Use 'Agg' for non-interactive server-side rendering
matplotlib.use('Agg')

# Design Tokens (Centralized for easy branding updates)
THEME = {
    "bg": "#050505",
    "text_primary": "#FAFAFA",
    "text_secondary": "#A1A1AA",
    "teal": "#00F5D4",
    "purple": "#8B5CF6",
    "grid": "#1A1A1A"
}

def _apply_dark_theme(ax: plt.Axes, fig: plt.Figure):
    """Utility to enforce brand consistency across all charts."""
    ax.set_facecolor(THEME["bg"])
    fig.patch.set_facecolor(THEME["bg"])
    ax.tick_params(colors=THEME["text_secondary"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", alpha=0.3, color=THEME["grid"], linestyle="--")

def build_risk_chart_png(risks_df: pd.DataFrame) -> bytes | None:
    """
    Renders risk chart as raw PNG bytes for UI stability and ZIP exports.
    """
    if risks_df.empty: return None

    plot_df = risks_df.sort_values("score", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.barh(plot_df["risk"].astype(str), plot_df["score"].astype(float), color=THEME["teal"], height=0.6)
    
    ax.set_xlabel("Risk Score", color=THEME["text_secondary"], fontweight="bold")
    ax.set_title("Top PM Risk Exposure", color=THEME["text_primary"], pad=15, fontweight="bold")
    
    _apply_dark_theme(ax, fig)
    fig.tight_layout()
    
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=160)
    plt.close(fig) # Explicit memory cleanup
    
    return buffer.getvalue()

def build_gantt_chart_png(schedule_df: pd.DataFrame) -> bytes | None:
    """
    Renders Gantt chart as raw PNG bytes. 
    Prevents Streamlit serialization crashes associated with returning plt.Figure.
    """
    if schedule_df.empty: return None

    frame = schedule_df.sort_values("start_day", ascending=True).copy()
    frame["start_day"] = pd.to_numeric(frame["start_day"], errors="coerce").fillna(0)
    frame["duration_days"] = pd.to_numeric(frame["duration_days"], errors="coerce").fillna(1)

    fig, ax = plt.subplots(figsize=(10, max(3, len(frame) * 0.55)))
    
    ax.barh(
        frame["task"].astype(str), frame["duration_days"], left=frame["start_day"], 
        color=THEME["purple"], height=0.4, edgecolor=THEME["teal"], linewidth=1.5
    )
    
    ax.set_xlabel("Project Day", color=THEME["text_secondary"], fontweight="bold")
    ax.set_title("Optimized Baseline Schedule", color=THEME["text_primary"], pad=15, fontweight="bold")
    
    _apply_dark_theme(ax, fig)
    ax.invert_yaxis()
    fig.tight_layout()
    
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=160)
    plt.close(fig)
    
    return buffer.getvalue()
