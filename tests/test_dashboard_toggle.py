from unittest.mock import patch


def test_demo_dataset_supports_offline_streamlit_demo():
    """Phase 1 demo must run with synthetic HVAC data and no Mongo dependency."""
    from streamlit_app import build_demo_dataset

    dataset = build_demo_dataset("Busy Monday")

    assert set(dataset) == {"jobs", "inventory", "ar"}
    assert "HP-001" in dataset["inventory"]["sku"].to_list()
    assert dataset["jobs"].iloc[0]["priority"] == "Emergency"


def test_simulation_result_contains_owner_value_and_agent_trace():
    """The one-click demo run should produce KPIs and a visible multi-agent trace."""
    from streamlit_app import build_demo_dataset, build_simulation_result

    result = build_simulation_result(build_demo_dataset("AR Cleanup"))

    assert result["total_monthly_savings"] >= 8400
    assert result["downtime_reduction"] == 0.42
    assert "LeadArchitect" in result["agent_trace"][0]


def test_live_mongo_toggle_copy_remains_in_parts_dashboard():
    """Parts dashboard keeps validated-schema toggle language from PROJECT_MEMORY.md canonical VP."""
    from streamlit_app import parts_availability_dashboard

    assert "PROJECT_MEMORY.md canonical VP" in parts_availability_dashboard.__doc__
    assert "Use Live Mongo toggle" in parts_availability_dashboard.__doc__
    assert "30-50% less downtime" in parts_availability_dashboard.__doc__


@patch("streamlit.checkbox")
@patch("streamlit.caption")
@patch("streamlit.dataframe")
@patch("streamlit.success")
@patch("streamlit.title")
def test_parts_availability_dashboard_renders_basic_controls(
    mock_title, mock_success, mock_dataframe, mock_caption, mock_checkbox
):
    from streamlit_app import parts_availability_dashboard

    parts_availability_dashboard()

    mock_title.assert_called_with("HVAC Parts Availability Command Center")
    mock_checkbox.assert_called()
    mock_dataframe.assert_called()
    mock_caption.assert_called()
    mock_success.assert_called()
