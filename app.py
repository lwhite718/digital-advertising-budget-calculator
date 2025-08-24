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

# --- Available Platforms ---
platform_options = ["Google Ads", "Meta Ads", "LinkedIn Ads", "Reddit Ads", "TikTok Ads"]

st.set_page_config(page_title="Marketing Budget Allocator", layout="centered")

st.title("🧮 Marketing Budget Allocator")
st.markdown("Use this tool to intelligently split your ad budget across platforms and campaign types.")

# --- TABS ---
tab1, tab2 = st.tabs(["📈 Single Campaign", "🧩 Multi-Campaign Allocation"])

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

    selected_platforms = st.multiselect(
        "Select Platforms to Include",
        platform_options,
        default=platform_options
    )

    funnel = goal_to_funnel.get(goal, "TOFU")

    # --- Feedback Section ---
    st.subheader("💡 Channel Fit Suggestions")

    for p in selected_platforms:
        if audience == "B2B" and p == "TikTok Ads":
            st.warning(f"{p} is generally not effective for B2B. You may want to reconsider.")
        if goal == "Sales" and p == "Reddit Ads":
            st.info(f"{p} can be weak for direct sales. Consider pairing with search or retargeting.")

    # --- Calculate ---
    if st.button("🚀 Calculate Allocation"):
        results = calculate_allocations(
            total_budget=total_budget,
            goal=goal,
            funnel=funnel,
            audience=audience,
            allowed_platforms=selected_platforms
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
        with st.expander(f"Channels for Campaign {i+1}"):
            selected = st.multiselect(f"Select Platforms", platform_options, default=platform_options, key=f"plat_{i}")
        multi_inputs.append({
            "goal": g,
            "audience": a,
            "platforms": selected
        })

    if st.button("📊 Run Multi-Campaign Allocation"):
        total_weight = sum(goal_weights[c["goal"]] for c in multi_inputs)

        for idx, campaign in enumerate(multi_inputs):
            weight = goal_weights[campaign["goal"]]
            budget_share = (weight / total_weight)
            allocated_budget = round(total_multi_budget * budget_share, 2)
            funnel = goal_to_funnel.get(campaign["goal"], "TOFU")

            st.markdown(f"### 🎯 Campaign {idx+1}: {campaign['goal']} ({campaign['audience']})")
            st.markdown(f"**Budget:** ${allocated_budget:,.2f} | Funnel: {funnel}")

            results = calculate_allocations(
                total_budget=allocated_budget,
                goal=campaign["goal"],
                funnel=funnel,
                audience=campaign["audience"],
                allowed_platforms=campaign["platforms"]
            )

            if "error" in results:
                st.error(results["error"])
            else:
                for res in results:
                    st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
                st.markdown("---")

# =============================
# SIDEBAR: DYNAMIC SUMMARY
# =============================
st.sidebar.title("📋 Summary")

if st.session_state.active_tab == "single":
    st.sidebar.write(f"Goal: {goal}")
    st.sidebar.write(f"Funnel: {funnel}")
    st.sidebar.write(f"Audience: {audience}")
    st.sidebar.write(f"Budget: ${total_budget:,.2f}")
    st.sidebar.write("Platforms:")
    for p in selected_platforms:
        st.sidebar.write(f"• {p}")

elif st.session_state.active_tab == "multi":
    st.sidebar.write(f"Campaigns: {num_campaigns}")
    st.sidebar.write(f"Total Budget: ${total_multi_budget:,.2f}")
