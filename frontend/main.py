import streamlit as st
import requests
import json
import time

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="APIA — Automotive Process Intelligence Agent",
    page_icon="",
    layout="wide"
)

st.title("Automotive Process Intelligence Agent")
st.caption("BMW Group | Defect Analysis Automation")

# ── Session state ─────────────────────────────────────────────────────────────
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "report_id" not in st.session_state:
    st.session_state.report_id = None
if "awaiting_review" not in st.session_state:
    st.session_state.awaiting_review = False

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Submit Defect", "Agent Trace", "Review & Approve"])

# ── Tab 1: Submit ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Submit a New Defect Report")

    col1, col2 = st.columns(2)

    with col1:
        vehicle_model = st.text_input("Vehicle Model", placeholder="e.g. BMW z4")
        year = st.number_input("Year", min_value=2000, max_value=2026, value=2022)
        mileage = st.number_input("Mileage (km)", min_value=0, value=45000, step=1000)

    with col2:
        error_codes_raw = st.text_input(
            "Error Codes (comma separated)",
            placeholder="e.g. P0300, P0301"
        )
        reported_by = st.text_input("Reported By", value="Engineer")

    symptom = st.text_area(
        "Symptom Description",
        placeholder="Describe the defect in detail — what the driver reported, when it occurs, any patterns...",
        height=120
    )

    if st.button("Analyse Defect", type="primary", use_container_width=True):
        if not symptom:
            st.error("Please describe the symptom.")
        else:
            error_codes = [c.strip() for c in error_codes_raw.split(",") if c.strip()]

            payload = {
                "vehicle_model": vehicle_model,
                "year": int(year),
                "mileage_km": int(mileage),
                "error_codes": error_codes,
                "symptom_description": symptom,
                "reported_by": reported_by
            }

            with st.spinner("Agent pipeline running... this takes 30-60 seconds"):
                try:
                    response = requests.post(
                        f"{API_URL}/submit-defect",
                        json=payload,
                        timeout=120
                    )
                    response.raise_for_status()
                    data = response.json()

                    st.session_state.current_report = data.get("report")
                    st.session_state.report_id = data.get("report_id")
                    st.session_state.thread_id = data.get("thread_id")
                    st.session_state.awaiting_review = True
                    st.session_state.classification = data.get("classification")
                    st.session_state.iteration = data.get("iteration", 1)

                    st.success(f"Report {data['report_id']} generated. Switch to **Review & Approve** tab.")
                    st.balloons()

                except Exception as e:
                    st.error(f"Error: {e}")

# ── Tab 2: Trace viewer (simplified) ─────────────────────────────────────────
with tab2:
    st.subheader("Agent Pipeline Trace")

    if st.session_state.current_report and st.session_state.classification:
        cl = st.session_state.classification

        st.markdown("### Pipeline Execution")

        steps = [
            ("1. Classify", f"Category: **{cl.get('defect_category', 'N/A')}** | "
                            f"Severity: **{cl.get('severity', 'N/A')}** | "
                            f"Known issue: **{cl.get('is_known_issue', False)}**",
             ""),
            ("2. Research", "Searched vector store + fetched relevant document sections", ""),
            ("3. Validate", "Checked IATF 16949 compliance + web search for recent updates", ""),
            ("4. Write Report", f"Report **{st.session_state.report_id}** generated", ""),
            ("5. Human Review", "Awaiting your approval (Review tab)", ""),
        ]

        for step_name, detail, status in steps:
            col_a, col_b, col_c = st.columns([2, 6, 1])
            with col_a:
                st.markdown(f"**{step_name}**")
            with col_b:
                st.markdown(detail)
            with col_c:
                st.markdown(status)
            st.divider()

        st.markdown("**Classification keywords used for RAG search:**")
        st.code(", ".join(cl.get("search_keywords", [])))
        st.markdown(f"*Classifier reasoning: {cl.get('reasoning', '')}*")

    else:
        st.info("Submit a defect on the first tab to see the agent trace here.")

# ── Tab 3: Review ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Review & Approve Generated Report")

    if not st.session_state.awaiting_review or not st.session_state.current_report:
        st.info("No report pending review. Submit a defect on the first tab.")
    else:
        report = st.session_state.current_report

        st.markdown(f"### Report `{report.get('report_id')}`")

        # Priority badge
        priority = report.get("priority", "routine").upper()
        colour = {"ROUTINE": "🟢", "URGENT": "🟡", "IMMEDIATE": "🔴"}.get(priority, "⚪")
        st.markdown(f"**Priority:** {colour} {priority}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Defect Category**")
            st.info(report.get("defect_category", "N/A").title())

            st.markdown("**Severity**")
            st.warning(report.get("severity", "N/A").upper())

            st.markdown("**Estimated Repair Time**")
            st.metric("Hours", report.get("estimated_hours", 0))

        with col2:
            st.markdown("**Root Cause**")
            st.write(report.get("root_cause", "N/A"))

            st.markdown("**Standards Compliance**")
            st.write(report.get("standards_compliance", "N/A"))

        st.markdown("**Recommended Action**")
        st.success(report.get("recommended_action", "N/A"))

        if report.get("required_parts"):
            st.markdown("**Required Parts**")
            for part in report["required_parts"]:
                st.markdown(f"• {part}")

        if report.get("warnings"):
            st.markdown("**⚠ Warnings**")
            for w in report["warnings"]:
                st.error(w)

        st.markdown("---")
        st.markdown("### Your Decision")

        feedback = st.text_area(
            "Feedback (required if rejecting)",
            placeholder="What should the agent research differently or fix?",
            height=80
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Approve Report", type="primary", use_container_width=True):
                with st.spinner("Saving report..."):
                    response = requests.post(f"{API_URL}/human-decision", json={
                        "report_id": st.session_state.report_id,
                        "approved": True,
                        "feedback": ""
                    })
                    if response.ok:
                        st.success("Report approved and saved. Word document generated in output/reports/")
                        st.session_state.awaiting_review = False
                    else:
                        st.error("Save failed.")

        with col_b:
            if st.button("Request Revision", use_container_width=True):
                if not feedback:
                    st.error("Please provide feedback explaining what to fix.")
                else:
                    with st.spinner("Sending to agent for revision..."):
                        response = requests.post(f"{API_URL}/human-decision", json={
                            "report_id": st.session_state.report_id,
                            "approved": False,
                            "feedback": feedback
                        })
                        if response.ok:
                            data = response.json()
                            st.session_state.current_report = data.get("report")
                            st.success(f"Revised! Iteration {data.get('iteration')}. Review the updated report above.")
                            st.rerun()
                        else:
                            st.error("Revision request failed.")