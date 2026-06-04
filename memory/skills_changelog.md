---
title: Skills Changelog
project: HVAC OpsForge Flagship
description: Log of all Hermes skill creations, patches, and updates related to the HVAC product.
last_updated: 2026-06-04
---

# Skills Changelog

[2026-06-04 09:00 EST] Initial Skills Created
Summary: 
- Created hvac-parts-availability-checker (devops category) with full TDD plan, report template, and integration guidance.
- Loaded writing-plans, test-driven-development, systematic-debugging, requesting-code-review for all future work.
Decision: All skills must be production-grade, follow existing architecture, and include verification checklist.
Status: Baseline established | Next changes will be logged with exact diffs and test results
---

[2026-06-04 10:30 EST] Git + Memory Configuration
Summary: Updated workflow for dev/ai-integration branch only. All future major changes (TDD cycles, skill integrations) will append to project_log.md and skills_changelog.md then commit+push. Memory scaffolding now active for flagship demos.
Status: Enforced in agent behavior | Ready for Parts Checker TDD implementation
---

[2026-06-04 21:35 EST] TDD RED Phase for hvac-parts-availability-checker
Summary: Loaded test-driven-development, writing-plans, hvac-parts-availability-checker skills. Added failing pytest tests in test_mongo.py for generate_pre_departure_report (2 tests covering report structure, synthetic fallback, validation per skill templates). Exact diff shown, tests run and confirmed failing (AttributeError on missing method). No implementation code added. Updated skills_changelog per rules. This enforces the RED-GREEN-REFACTOR cycle and surgical changes to InventoryForecasterAgent + MongoDBTools.
Status: RED complete | Tests valid and failing | Changelog updated with TDD verification
---
