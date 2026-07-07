# views/ar_operations.py
import streamlit as st
import pandas as pd

def render_ar_operations() -> None:
    """Renders the Accounts Receivable and cashflow operations dashboard."""
    
    st.markdown('<div class="section-kicker">Financial Operations</div>', unsafe_allow_html=True)
    st.title("AR Follow-up Queue")
    
    result = st.session_state.get("pm_result")
    
    if not result:
        st.markdown('<div class="glass-card" style="padding: 2rem; text-align: center;">', unsafe_allow_html=True)
        st.warning("No active baseline found. Please run the orchestrator in the Dispatch Workspace first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    invoices = result.get("overdue_invoices", [])
    if not invoices:
        st.success("Zero overdue invoices in the current baseline queue! 🎉")
        return

    df = pd.DataFrame(invoices)
    total_overdue = df['amount'].sum() if 'amount' in df.columns else 0

    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">', unsafe_allow_html=True)
    st.metric("Total Exposed Capital", f"${total_overdue:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Action Required")
    
    for idx, row in df.iterrows():
        invoice_id = row.get("invoice_id", f"INV-{idx}")
        customer = row.get("customer_name", "Unknown Customer")
        amount = row.get("amount", 0.0)
        days = row.get("days_overdue", 0)
        
        decision_key = f"ar_decision_{invoice_id}"
        current_decision = st.session_state.get(decision_key, "Pending")

        with st.container():
            st.markdown('<div class="glass-card" style="padding: 1rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2], vertical_alignment="center")
            
            with col1:
                st.markdown(f"**{customer}** ({invoice_id})")
                st.caption(f"${amount:,.2f} — {days} days overdue")
                
            with col2:
                if current_decision == "Approved":
                    st.success("Approved")
                elif current_decision == "Rejected":
                    st.error("Rejected")
                else:
                    if st.button("Approve Action", key=f"app_{invoice_id}", use_container_width=True):
                        st.session_state[decision_key] = "Approved"
                        st.rerun()
                        
            with col3:
                if current_decision == "Pending":
                    if st.button("Reject", key=f"rej_{invoice_id}", use_container_width=True):
                        st.session_state[decision_key] = "Rejected"
                        st.rerun()
                        
            st.markdown('</div>', unsafe_allow_html=True)