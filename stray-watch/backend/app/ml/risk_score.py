def calculate_risk_score(total: int, vaccinated: int, days_since_survey: int) -> int:
    """
    Calculates a risk score (0-100) for a locality.
    Higher score = more dangerous = needs urgent attention.

    Three factors are combined:

    FACTOR 1 — Vaccination coverage (max 50 points)
    ─────────────────────────────────────────────────
    This is the most important factor.
    If only 30% of dogs are vaccinated, coverage = 0.30
    Score contribution = (1 - 0.30) * 50 = 35 points
    If 90% vaccinated: (1 - 0.90) * 50 = 5 points (low risk)
    If 0% vaccinated:  (1 - 0.00) * 50 = 50 points (max risk)

    FACTOR 2 — Days since last survey (max 36 points)
    ──────────────────────────────────────────────────
    Stale data = we don't know the real situation = higher risk.
    Capped at 30 days so old surveys don't inflate the score infinitely.
    Surveyed today:    0 * 1.2 = 0 points
    Surveyed 15 days ago: 15 * 1.2 = 18 points
    Surveyed 30+ days ago: 30 * 1.2 = 36 points (max)

    FACTOR 3 — Population size (max 14 points)
    ────────────────────────────────────────────
    More dogs in an area = more risk surface even if coverage is decent.
    Normalized so 100 dogs = full 14 points.
    10 dogs:  (10/100) * 14 = 1.4 points
    50 dogs:  (50/100) * 14 = 7 points
    100+ dogs: capped at 14 points
    """

    if total == 0:
        return 0  # no dogs = no risk

    vax_coverage = vaccinated / total  # e.g. 0.38 for 38% vaccinated

    # Factor 1: low vaccination = high risk
    coverage_score = (1 - vax_coverage) * 50

    # Factor 2: how long since this locality was physically checked
    survey_score = min(days_since_survey, 30) * 1.2

    # Factor 3: raw population size (normalized, capped at 1.0)
    population_score = min(total / 100, 1.0) * 14

    raw = coverage_score + survey_score + population_score

    # Final score is always between 0 and 100
    final_score = min(round(raw), 100)

    return final_score


def get_risk_label(score: int) -> str:
    """
    Converts a numeric score into a human-readable label.
    Used for the colored badges in the frontend.
    """
    if score >= 70:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"