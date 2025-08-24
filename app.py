import streamlit as st
from budget_allocator import calculate_allocations

st.set_page_config(page_title="Marketing Budget Allocator", layout="centered")

st.title("🧮 Marketing Budget Allocator")
st.markdown("Use this tool to intelligently split your ad budget based on strategic inputs.")

# --- INPUTS ---
st.subheader("🔧 Campaign Inputs")

total_budget = st.number_input("Total Ad Budget ($)", min_value=1000, value=5000, step=500)

goal_options = ["Awareness", "Engagement", "Lead Gen", "Sales"]
funnel_options = ["TOFU", "MOFU", "BOFU"]
audience_options = ["B2B", "B2C"]

col1, col2 = st.columns(2)

with col1:
    funnel = st.selectbox("Funnel Focus", funnel_options)

with col2:
    # Only show Engagement if TOFU is selected
    if funnel != "TOFU":
        goal_options_display = [g for g in goal_options if g != "Engagement"]
    else:
        goal_options_display = goal_options

    goal = st.selectbox("Marketing Goal", goal_options_display)

audience = st.selectbox("Audience Type", audience_options)
retargeting_enabled = st.checkbox("Include retargeting allocation (Google Display)")

# --- DEBUG PANEL ---
st.sidebar.title("🔍 Debug Panel")
st.sidebar.write(f"Goal: {goal}")
st.sidebar.write(f"Funnel: {funnel}")
st.sidebar.write(f"Audience: {audience}")
st.sidebar.write(f"Retargeting: {retargeting_enabled}")
st.sidebar.write(f"Total Budget: ${total_budget}")

# --- ALLOCATION CALC ---
if st.button("🚀 Calculate Allocation"):
    results = calculate_allocations(
        total_budget=total_budget,
        goal=goal,
        funnel=funnel,
        audience=audience,
        retargeting_enabled=retargeting_enabled
    )

    if "error" in results:
        st.error(results["error"])
    else:
        st.subheader("📊 Budget Breakdown")
        st.markdown(f"**Total Budget:** ${total_budget:,.2f}")

        for res in results:
            st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
            if "notes" in res:
                st.caption(res["notes"])
