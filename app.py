import streamlit as st
from budget_allocator import calculate_allocations
from channel_config import channel_scores

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

# --- TABS ---
tab1, tab2 = st.tabs(["📈 Single Campaign", "🧩 Multi-Campaign Allocation"])

# =============================
# TAB 1: SINGLE CAMPAIGN
# =============================
with tab1:
    st.session_state.active_tab = "single"

    st.subheader("🔧 Single Campaign Setup")

    total_budget = st.number_input("Total Budget for This Campaign ($)", min_value=0, value=0, step=500)
    goal = st.selectbox("Campaign Goal", list(goal_to_funnel.keys()))
    audience = st.selectbox("Audience Type", ["B2B", "B2C"])
    selected_platform = st.selectbox("Which platform will this campaign run on?", platform_options)

    funnel = goal_to_funnel.get(goal, "TOFU")

    st.subheader("💡 Platform Fit Feedback")
    if audience == "B2B" and selected_platform == "TikTok Ads":
        st.warning("TikTok Ads is generally not effective for B2B campaigns.")
    if goal == "Sales" and selected_platform == "Reddit Ads":
        st.info("Reddit Ads is not commonly used for direct sales.")

    if st.button("🚀 Run Allocation", key="single_run"):
        try:
            results = calculate_allocations(
                total_budget=total_budget,
                goal=goal,
                funnel=funnel,
                audience=audience,
                allowed_platforms=[selected_platform]
            )

            if "error" in results:
                st.error(results["error"])
            else:
                st.subheader("📊 Budget Breakdown")
                for res in results:
                    st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
                    if "notes" in res:
                        st.caption(res["notes"])
        except Exception as e:
            st.error(f"Backend error: {e}")

# =============================
# TAB 2: MULTI-CAMPAIGN
# =============================
with tab2:
    st.session_state.active_tab = "multi"

    st.subheader("🧩 Multi-Campaign Setup")

    total_multi_budget = st.number_input("Total Budget for All Campaigns ($)", min_value=0, value=0, step=500)
    available_platforms = st.multiselect("Which platforms are available for your campaigns?", platform_options)
    recommend_platforms = st.checkbox("🧠 Recommend best-fit platforms for each campaign?")

    num_campaigns = st.slider("Number of Campaigns", 2, 5, 2)

    campaign_configs = []
    for i in range(num_campaigns):
        st.markdown(f"#### Campaign {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            g = st.selectbox(f"Goal {i+1}", list(goal_to_funnel.keys()), key=f"goal_{i}")
        with col2:
            a = st.selectbox(f"Audience {i+1}", ["B2B", "B2C"], key=f"aud_{i}")

        if not recommend_platforms:
            if available_platforms:
                with st.expander(f"Select Platform for Campaign {i+1}"):
                    p = st.selectbox(f"Platform", available_platforms, key=f"plat_{i}")
            else:
                st.warning("Please select at least one platform to continue.")
                p = None
        else:
            p = None

        campaign_configs.append({"goal": g, "audience": a, "platform": p})

    if st.button("📊 Run Multi-Campaign Allocation", key="multi_run"):
        total_weight = sum(goal_weights[c["goal"]] for c in campaign_configs)

        for idx, campaign in enumerate(campaign_configs):
            goal = campaign["goal"]
            audience = campaign["audience"]
            weight = goal_weights[goal]
            budget_share = weight / total_weight
            allocated_budget = round(total_multi_budget * budget_share, 2)
            funnel = goal_to_funnel[goal]

            if recommend_platforms and available_platforms:
                scored = []
                for p in available_platforms:
                    base = channel_scores[p]["base_scores"].get(goal, 0)
                    aud_mod = channel_scores[p]["modifiers"].get(audience, 0)
                    fun_mod = channel_scores[p]["modifiers"].get(funnel, 0)
                    score = base + aud_mod + fun_mod
                    scored.append((p, score))
                scored = [x for x in scored if x[1] > 0]
                best_platform = scored[0][0] if scored else available_platforms[0]
            else:
                best_platform = campaign["platform"] if campaign["platform"] else "Unknown"

            st.markdown(f"### 🎯 Campaign {idx+1}: {goal} ({audience})")
            st.markdown(f"**Assigned Platform:** {best_platform}")
            st.markdown(f"**Budget:** ${allocated_budget:,.2f} | Funnel: {funnel} | Share: {round(budget_share * 100, 1)}%")

            try:
                results = calculate_allocations(
                    total_budget=allocated_budget,
                    goal=goal,
                    funnel=funnel,
                    audience=audience,
                    allowed_platforms=[best_platform]
                )

                if "error" in results:
                    st.error(results["error"])
                else:
                    for res in results:
                        st.write(f"**{res['platform']}** — {res['percent']}% → ${res['budget']:,.2f}")
                    st.markdown("---")
            except Exception as e:
                st.error(f"Backend error: {e}")

# =============================
# SIDEBAR: DYNAMIC SUMMARY
# =============================
st.sidebar.title("📋 Campaign Summary")

if st.session_state.get("active_tab") == "single":
    st.sidebar.markdown("**Single Campaign Summary**")
    st.sidebar.write(f"Goal: {goal}")
    st.sidebar.write(f"Funnel: {funnel}")
    st.sidebar.write(f"Audience: {audience}")
    st.sidebar.write(f"Platform: {selected_platform}")
    st.sidebar.write(f"Budget: ${total_budget:,.2f}")

elif st.session_state.get("active_tab") == "multi":
    st.sidebar.markdown("**Multi-Campaign Summary**")
    st.sidebar.write(f"Campaigns: {num_campaigns}")
    st.sidebar.write(f"Total Budget: ${total_multi_budget:,.2f}")
    if available_platforms:
        st.sidebar.write("Selected Platforms:")
        for p in available_platforms:
            st.sidebar.write(f"• {p}")
