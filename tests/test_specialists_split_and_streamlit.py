"""TDD test for Phase 2: specialists split + Streamlit Parts Availability Dashboard.
RED watched first (structure missing, dashboard NotImplemented). GREEN after split and dashboard fn.
REFACTOR: clean imports, registry re-export. JTBD + Porter's in log.
"""

import os
from unittest.mock import patch

import pytest

from core.agents.specialists import SPECIALISTS


def test_split_structure_exists():
    """GREEN: Subpackage with individual files + registry in __init__.py."""
    assert os.path.exists("core/agents/specialists/__init__.py")
    expected = [
        "inventory_forecaster.py",
        "risk_assessor.py",
        "scheduler_optimizer.py",
        "ar_collector.py",
        "parts_availability_checker.py",
    ]
    for f in expected:
        assert os.path.exists(f"core/agents/specialists/{f}")
    assert len(SPECIALISTS) >= 5
    assert "parts_availability_checker" in SPECIALISTS


def test_registry_in_init_after_split():
    """GREEN: Dynamic registry works post-split."""
    assert callable(SPECIALISTS["parts_availability_checker"].execute)


@patch("streamlit.title")
@patch("streamlit.checkbox")
@patch("streamlit.dataframe")
@patch("streamlit.success")
@patch("streamlit.caption")
def test_streamlit_parts_dashboard(
    mock_caption, mock_success, mock_dataframe, mock_checkbox, mock_title
):
    """GREEN: Dashboard keeps the parts view callable with HVAC value metrics."""
    from streamlit_app import parts_availability_dashboard

    parts_availability_dashboard()
    mock_title.assert_called_with("HVAC Parts Availability Command Center")
    mock_checkbox.assert_called()
    mock_dataframe.assert_called()
    mock_caption.assert_called()
    mock_success.assert_called()


# Run with: python -m pytest this_file -q
if __name__ == "__main__":
    pytest.main([__file__, "-q"])
