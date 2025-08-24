import streamlit as st
from budget_allocator import calculate_allocations

# --- Goal-to-Funnel Mapping ---
goal_to_funnel = {
    "Awareness": "TOFU",
    "Engagement": "TOFU",
    "Lead Gen": "MOFU",
    "Sales": "BOFU"
}

# --- Budget Weight by Goal ---
goal_weights = {
    "Awareness": 1.0,
    "Engagement": 0.8,
    "Lead Gen": 1.2,
    "Sales": 1.5
}

st.set_page_config(page_title="Marketing Budget Allocator", layout="centered")

st.title("🧮 Marketing Budget Allocator")
st.markdown("Use this tool to intelligently split your ad budget across platforms and campaign types.")

# --- TABS ---
tab1, tab2 = st.tabs(["📈 Single Campaign", "🧩 Multi-Campaign Allocation"])

# Store active tab in session
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "single"

# =============================
# TAB 1: SINGLE CAMPAIGN
# =============================
with tab1:
    st.session_state.active_tab = "single"

    st.subheader("🔧 Campaign Inputs")

    total_budget = st.number_input("Total Ad Budget ($)", min_value=1000, value=5000, step=500)

    goal_options = list(goal_to_funnel.keys())
    audience_options = ["B2B", "B2C"]

    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Marketing Goal", goal_options)
    with col2:
        audience = st.selectbox("Audience Type", audience_options)

    funnel = goal_to_funnel.get(goal, "TOFU")

    if st.button("🚀 Calculate Allocation"):
        results = calculate_allocations(
            total_budget=total_budget,
            goal=goal,
            funnel=funnel,
            audience=audience
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

# =============================
# TAB 2: MULTI-CAMPAIGN
# =============================
with tab2:
    st.session_state.active_tab = "multi"

    st.subheader("🧪 Multi-Campaign Allocation (Auto Budget)")

    st.markdown("Define multiple campaign types — the system will auto-allocate your budget based on each goal's strategic weight.")

    total_multi_budget = st.number_input("Total Budget for All Campaigns ($)", min_value=2000, value=10000, step=500)

    num_campaigns = st.slider("How many campaigns?", 2, 5, 2)

    goal_options = list(goal_to_funnel.keys())
    audience_options = ["B2B", "B2C"]
    multi_inputs = []

    for i in range(num_campaigns):
        st.markdown(f"#### Campaign {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            g = st.selectbox(f"Goal {i+1}", goal_options, key=f"goal_{i}")
        with col2:
            a = st.selectbox(f"Audience {i+1}", audience_options, key=f"aud_{i}")
        multi_inputs.append({"goal": g, "audience": a})

    if st.button("📊 Run Multi-Campaign Allocation"):
        # Calculate weights
        total_weight = sum(goal_weights[c["goal"]] for c in multi_inputs)

        for idx, campaign in enumerate(multi_inputs):
            weight = goal_weights[campaign["goal"]]
            budget_share = (weight / total_weight)
            allocated_budget = round(total_multi_budget * budget_share, 2)

            st.markdown(f"### 🎯 Campaign {idx+1}: {campaign['goal']}")
            funnel = goal_to_funnel.get(campaign["goal"], "TOFU")

            results = calculate_allocations(
                total_budget=allocated_budget,
                goal=campaign["goal"],
                funnel=funnel,
                audience=campaign["audience"]
            )

            if "error" in results:
                st.error(results["error"])
            else:
                st.markdown(f"**Campaign Budget:** ${allocated_budget:,.2f}")
                for res in results:
                    st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
                st.markdown("---")

# =============================
# SIDEBAR: SUMMARY PANEL
# =============================
st.sidebar.title("📋 Summary")

if st.session_state.active_tab == "single":
    st.sidebar.write(f"Goal: {goal}")
    st.sidebar.write(f"Funnel: {funnel}")
    st.sidebar.write(f"Audience: {audience}")
    st.sidebar.write(f"Total Budget: ${total_budget:,.2f}")

elif st.session_state.active_tab == "multi":
    st.sidebar.write(f"Campaigns: {num_campaigns}")
    st.sidebar.write(f"Total Budget: ${total_multi_budget:,.2f}")
