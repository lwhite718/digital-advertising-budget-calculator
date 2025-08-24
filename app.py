import streamlit as st
from budget_allocator import calculate_allocations

# --- Goal-to-Funnel Mapping ---
goal_to_funnel = {
    "Awareness": "TOFU",
    "Engagement": "TOFU",
    "Lead Gen": "MOFU",
    "Sales": "BOFU"
}

st.set_page_config(page_title="Marketing Budget Allocator", layout="centered")

st.title("🧮 Marketing Budget Allocator")
st.markdown("Use this tool to intelligently split your ad budget across platforms based on campaign goals.")

# --- TABS ---
tab1, tab2 = st.tabs(["📈 Single Campaign", "🧩 Multi-Campaign Allocation"])

# =============================
# TAB 1: SINGLE CAMPAIGN
# =============================
with tab1:
    st.subheader("🔧 Campaign Inputs")

    total_budget = st.number_input("Total Ad Budget ($)", min_value=1000, value=5000, step=500)

    goal_options = list(goal_to_funnel.keys())
    audience_options = ["B2B", "B2C"]

    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Marketing Goal", goal_options)
    with col2:
        audience = st.selectbox("Audience Type", audience_options)

    # Map goal to funnel internally
    funnel = goal_to_funnel.get(goal, "TOFU")

    # --- SUMMARY PANEL ---
    st.sidebar.title("📋 Campaign Summary")
    st.sidebar.write(f"Goal: {goal}")
    st.sidebar.write(f"Funnel: {funnel}")
    st.sidebar.write(f"Audience: {audience}")
    st.sidebar.write(f"Total Budget: ${total_budget:,.2f}")

    # --- CALCULATE ---
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
# TAB 2: MULTI-CAMPAIGN (PREVIEW)
# =============================
with tab2:
    st.subheader("🧪 Multi-Campaign Allocation (Preview)")

    st.markdown("Allocate your total budget across multiple campaign types.")

    total_multi_budget = st.number_input("Total Budget for All Campaigns ($)", min_value=2000, value=10000, step=500)

    # Example: Let user define 2 campaigns
    num_campaigns = st.slider("How many campaigns?", 2, 5, 2)

    multi_inputs = []
    col_names = ["Campaign Goal", "Audience", "Budget %"]
    st.markdown("### 📋 Campaign Configurations")

    for i in range(num_campaigns):
        st.markdown(f"#### Campaign {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            g = col1.selectbox(f"Goal {i+1}", goal_options, key=f"goal_{i}")
        with col2:
            a = col2.selectbox(f"Audience {i+1}", audience_options, key=f"aud_{i}")
        with col3:
            pct = col3.slider(f"Budget % {i+1}", 10, 100, 50, key=f"pct_{i}")
        multi_inputs.append({"goal": g, "audience": a, "percent": pct})

    if st.button("📊 Run Multi-Campaign Allocation"):
        total_pct = sum(c["percent"] for c in multi_inputs)
        if total_pct != 100:
            st.error("Total budget percentages across all campaigns must equal 100%.")
        else:
            for idx, campaign in enumerate(multi_inputs):
                st.markdown(f"### 🎯 Campaign {idx+1}: {campaign['goal']}")
                mapped_funnel = goal_to_funnel.get(campaign["goal"], "TOFU")
                allocated_budget = total_multi_budget * (campaign["percent"] / 100)

                results = calculate_allocations(
                    total_budget=allocated_budget,
                    goal=campaign["goal"],
                    funnel=mapped_funnel,
                    audience=campaign["audience"]
                )

                if "error" in results:
                    st.error(results["error"])
                else:
                    st.markdown(f"**Campaign Budget:** ${allocated_budget:,.2f}")
                    for res in results:
                        st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
