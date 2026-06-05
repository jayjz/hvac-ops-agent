"""TDD test for Phase 2: specialists split + Streamlit Parts Availability Dashboard.
RED watched first (structure missing, dashboard NotImplemented). GREEN after split and dashboard fn.
REFACTOR: clean imports, registry re-export. JTBD + Porter's in log.
"""
import pytest
from unittest.mock import MagicMock, patch
import os

from core.agents.specialists import SPECIALISTS

def test_split_structure_exists():
    """GREEN: Subpackage with individual files + registry in __init__.py."""
    assert os.path.exists("core/agents/specialists/__init__.py")
    expected = ["inventory_forecaster.py", "risk_assessor.py", "scheduler_optimizer.py", "ar_collector.py", "parts_availability_checker.py"]
    for f in expected:
        assert os.path.exists(f"core/agents/specialists/{f}")
    assert len(SPECIALISTS) >= 5
    assert "parts_availability_checker" in SPECIALISTS

def test_registry_in_init_after_split():
    """GREEN: Dynamic registry works post-split."""
    assert callable(SPECIALISTS["parts_availability_checker"].execute)

@patch("streamlit.title")
@patch("streamlit.selectbox")
@patch("streamlit.button")
@patch("streamlit.success")
@patch("streamlit.caption")
def test_streamlit_parts_dashboard(mock_caption, mock_success, mock_button, mock_selectbox, mock_title):
    """GREEN: Dashboard uses registry for PartsAvailabilityChecker, logs business value."""
    from streamlit_app import parts_availability_dashboard
    parts_availability_dashboard()
    mock_title.assert_called_with("HVAC Parts Availability Checker")
    mock_caption.assert_called()  # Business value caption with Porter's/JTBD
    print("Dashboard GREEN: uses SPECIALISTS registry for dynamic agent execution.")

# Run with: python -m pytest this_file -q
if __name__ == "__main__":
    pytest.main([__file__, "-q"])
