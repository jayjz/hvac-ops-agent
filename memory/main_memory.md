---
title: Main Memory
project: HVAC OpsForge Flagship
description: Core persistent context, business rules, key decisions, and high-level state for the HVAC operations AI product.
last_updated: 2026-06-04
---

# Main Memory Log

[2026-06-04 09:00 EST] Project Scaffolding Complete
Summary: Created memory scaffolding system per user requirements. All future responses will append important context/decisions/reports to the appropriate memory file with EST timestamp. Initial HVAC Business Context loaded from persistent memory.
Status: Scaffolding complete | Ready for production-grade development
Key Rules: 
- At start of every new session: read and summarize last 3 entries from main_memory.md and project_log.md
- Append to correct file only (main for high-level, project_log for decisions, parts_availability_reports for reports, skills_changelog for skill changes)
- Maintain production quality, clean architecture, TDD, and existing multi-agent pattern.
---
