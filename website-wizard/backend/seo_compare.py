def compare_seo(before: dict, after: dict) -> dict:
    """
    Compare two SEO audit results (before vs after)
    """

    # -------------------------
    # SCORE & GRADE CHANGE
    # -------------------------
    score_before = before.get("score", 0)
    score_after = after.get("score", 0)

    grade_before = before.get("grade", "N/A")
    grade_after = after.get("grade", "N/A")

    # -------------------------
    # CATEGORY COMPARISON
    # -------------------------
    category_changes = {}

    before_categories = before.get("category_scores", {})
    after_categories = after.get("category_scores", {})

    for category in set(before_categories) | set(after_categories):
        b = before_categories.get(category, 0)
        a = after_categories.get(category, 0)

        category_changes[category] = {
            "before": b,
            "after": a,
            "change": a - b
        }

    # -------------------------
    # ISSUE COMPARISON
    # -------------------------
    before_issues = {i["issue"] for i in before.get("issues", [])}
    after_issues = {i["issue"] for i in after.get("issues", [])}

    resolved = sorted(before_issues - after_issues)
    added = sorted(after_issues - before_issues)

    # -------------------------
    # EXECUTIVE SUMMARY
    # -------------------------
    if score_after > score_before:
        summary = "SEO improved after changes were applied."
    elif score_after < score_before:
        summary = "SEO performance declined after changes."
    else:
        summary = "SEO score remained unchanged."

    return {
        "score_change": score_after - score_before,
        "grade_change": f"{grade_before} → {grade_after}",
        "category_changes": category_changes,
        "issues_resolved": resolved,
        "issues_added": added,
        "summary": summary
    }
