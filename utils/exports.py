# utils/exports.py
import pandas as pd
from typing import Any, Dict
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

# Import the core QuickBooks logic
from core.dispatch_baseline import render_quickbooks_excel_export

def build_dispatch_baseline_download_zip(markdown_report: str, json_report: str) -> bytes:
    """
    Bundles the executive markdown and raw JSON baseline into a downloadable ZIP.
    """
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("dispatch_baseline.md", markdown_report)
        archive.writestr("dispatch_baseline.json", json_report)
    return output.getvalue()

def build_report_zip(
    report: Dict[str, Any],
    requirements_df: pd.DataFrame,
    risks_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    risk_chart_bytes: bytes | None,
) -> bytes:
    """
    The master archive generator. Bundles all CSVs, the summary, and charts 
    into a single operations package.
    """
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        if not requirements_df.empty:
            archive.writestr("hvac_requirements.csv", requirements_df.to_csv(index=False))
        if not risks_df.empty:
            archive.writestr("hvac_risks.csv", risks_df.to_csv(index=False))
        if not schedule_df.empty:
            archive.writestr("hvac_schedule.csv", schedule_df.to_csv(index=False))
            
        if risk_chart_bytes:
            archive.writestr("hvac_risk_chart.png", risk_chart_bytes)
            
        archive.writestr("hvac_executive_summary.md", _build_summary_markdown(report))
        
    return output.getvalue()

def _build_summary_markdown(report: Dict[str, Any]) -> str:
    """Generates a clean markdown summary for the ZIP bundle."""
    actions = report.get("recommended_actions", [])
    critical_path = report.get("critical_path", [])
    
    lines = [
        "# HVAC OpsForge Executive Summary",
        "",
        report.get("summary", "No summary returned."),
        "",
        f"- **Requirements:** {report.get('requirements_count', 'n/a')}",
        f"- **High Risks:** {report.get('high_risk_count', 'n/a')}",
        f"- **Planned Duration:** {report.get('planned_duration_days', 'n/a')} days",
    ]
    
    if critical_path:
        lines.extend(["", "## Critical Path", " -> ".join(str(item) for item in critical_path)])
    
    if actions:
        lines.extend(["", "## Recommended Actions"])
        lines.extend([f"- {action}" for action in actions])
        
    return "\n".join(lines)

def build_quickbooks_xlsx(baseline_data: Dict[str, Any]) -> bytes | None:
    """
    Wraps the core dispatch baseline logic to generate a QuickBooks-compatible 
    Excel workbook containing Invoices, Schedule, and Parts.
    """
    if not baseline_data:
        return None
    return render_quickbooks_excel_export(baseline_data)
