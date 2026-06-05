# Next Demo Step Proposal: Streamlit Integration for PartsAvailabilityChecker

**Goal**: Make PartsAvailabilityCheckerAgent interactive in the existing Streamlit app (streamlit_app.py) for flagship HVAC demo.
**TDD Approach** (per skill): 
1. Red test in tests/test_streamlit.py for UI components (part check form, results display, Mongo integration).
2. Green: Add page/section in streamlit_app.py using st.form, st.dataframe for PartCheckResult, call agent.execute via session_state.
3. Refactor: Add sidebar for job selection, real-time Mongo sync, visualization of availability_score/reorder_recommendations.

**Key Changes** (do not implement yet — propose only):
- New route/tab "Parts Availability Checker".
- Input: job_type, required_parts (multi-select from inventory).
- Output: availability_score gauge, urgency-colored table, reorder button that updates Mongo.
- Use registry: `agent_cls = SPECIALISTS["parts_availability_checker"](); result = await agent_cls.execute(...)`.
- Error handling, progress bars, export CSV.

**Benefits**: Demo-ready end-to-end flow (LeadArchitect plan → dynamic specialist → Streamlit UI → Mongo closeout). Aligns with clean architecture (UI as infrastructure layer).

**Estimated**: 4-6 TDD cycles. Run on dev/ai-integration only. Follow with brutal review.

Next: Approve → implement with terminal edits + auto-log.
