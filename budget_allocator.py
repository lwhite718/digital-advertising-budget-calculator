from channel_config import channel_scores

def calculate_allocations(total_budget, goal, funnel, audience, allowed_platforms=None):
    raw_scores = {}

    # Filter channels based on allowed_platforms
    channels = allowed_platforms if allowed_platforms else list(channel_scores.keys())

    for platform in channels:
        base = channel_scores[platform]["base_scores"].get(goal, 0)
        aud_mod = channel_scores[platform]["modifiers"].get(audience, 0)
        fun_mod = channel_scores[platform]["modifiers"].get(funnel, 0)
        total_score = base + aud_mod + fun_mod
        if total_score > 0:
            raw_scores[platform] = total_score

    total = sum(raw_scores.values())
    if total == 0:
        return {"error": "All scores calculated as zero. Please adjust inputs or check channel config."}

    results = []
    for platform, score in raw_scores.items():
        percent = score / total
        budget_split = round(percent * total_budget, 2)
        results.append({
            "platform": platform,
            "score": score,
            "percent": round(percent * 100, 1),
            "budget": budget_split
        })

    return sorted(results, key=lambda x: x["budget"], reverse=True)
