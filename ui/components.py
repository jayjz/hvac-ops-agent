"""
ui/components.py

Reusable "Spatial Cyber-Physical" UI primitives built on top of the CSS
classes injected by ui/styles.py. Keep views/*.py free of raw HTML — call
these instead so the visual language stays consistent app-wide.

Import pattern:
    from ui.components import hero_header, status_badge, kanban_card, ai_insight_panel
"""

import html
import streamlit as st
from typing import Literal

BadgeKind = Literal["success", "warning", "danger", "neutral"]


def hero_header(title: str, subtitle: str = "", right_slot: str = "") -> None:
    """Full-width glass hero banner for the top of a view."""
    st.markdown(
        f"""
        <div class="op-hero">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <p class="op-hero-title">{html.escape(title)}</p>
                    <p class="op-hero-sub">{html.escape(subtitle)}</p>
                </div>
                <div>{right_slot}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, kind: BadgeKind = "neutral") -> str:
    """Returns an HTML badge string — embed inside other component strings."""
    return f'<span class="op-badge op-badge-{kind}">{html.escape(label)}</span>'


def kanban_card(
    title: str,
    subtitle: str,
    badge_label: str,
    badge_kind: BadgeKind = "neutral",
    footer_left: str = "",
    footer_right: str = "",
) -> None:
    """Single job/schedule card for the dispatch Kanban board. Renders a closed HTML block."""
    st.markdown(
        f"""
        <div class="op-glass" style="padding:14px 16px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; font-family:'Space Grotesk';">{html.escape(title)}</span>
                {status_badge(badge_label, badge_kind)}
            </div>
            <div style="color:var(--text-secondary); font-size:0.85rem; margin-top:4px;">
                {html.escape(subtitle)}
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:10px;
                        font-size:0.78rem; color:var(--text-muted); border-top:1px solid var(--border-glass); padding-top:8px;">
                <span>{html.escape(footer_left)}</span>
                <span>{html.escape(footer_right)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_insight_panel(insights: list[dict]) -> None:
    """
    Renders the AI insights sidebar panel.
    insights: [{"icon": "⚠️", "text": "...", "kind": "warning"}, ...]
    """
    rows = ""
    for item in insights:
        kind = item.get("kind", "neutral")
        rows += f"""
        <div style="display:flex; gap:10px; padding:10px 0; border-bottom:1px solid var(--border-glass);">
            <span style="font-size:1.1rem;">{item.get('icon', '🤖')}</span>
            <span style="font-size:0.85rem; color:var(--text-secondary); line-height:1.4;">
                {html.escape(item['text'])} {status_badge(kind.upper(), kind)}
            </span>
        </div>
        """
    st.markdown(
        f"""
        <div class="op-glass op-glass-elevated" style="padding:18px 20px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="font-weight:700; font-family:'Space Grotesk';
                             background:linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
                             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    AI Insights
                </span>
            </div>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_item_html(icon: str, label: str, active: bool = False) -> str:
    """Renders custom styled sidebar navigation items."""
    cls = "op-nav-item active" if active else "op-nav-item"
    return f'<div class="{cls}"><span>{icon}</span><span>{html.escape(label)}</span></div>'
