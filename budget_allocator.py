from channel_config import channel_scores

def calculate_allocations(
    total_budget: float,
    goal: str,
    funnel: str,
    audience: str,
    exclude_engagement_if_invalid=True
):
    # Engagement only allowed with TOFU
    if exclude_engagement_if_invalid and goal == "Engagement" and funnel != "TOFU":
        return {"error": "Engagement is only allowed when Funnel Focus is Top-of-Funnel (TOFU)."}

    raw_scores = {}
    
    # Step 1: Calculate total score for each platform
    for platform, data in channel_scores.items():
        base = data["base_scores"].get(goal, 0)
        audience_mod = data["modifiers"].get(audience, 0)
        funnel_mod = data["modifiers"].get(funnel, 0)
        total_score = base + audience_mod + funnel_mod
        raw_scores[platform] = max(0, total_score)  # prevent negatives

    total = sum(raw_scores.values())
    
    if total == 0:
        return {"error": "Invalid combination. All scores calculated as zero."}

    # Step 2: Normalize to get percentages
    results = []
    for platform, score in raw_scores.items():
        percent = (score / total)
        budget_split = round(percent * total_budget, 2)
        results.append({
            "platform": platform,
            "score": score,
            "percent": round(percent * 100, 1),
            "budget": budget_split
        })

    return sorted(results, key=lambda x: x["budget"], reverse=True)
