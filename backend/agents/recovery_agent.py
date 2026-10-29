import os

try:
    from backend.services.llm import generate
except ModuleNotFoundError:
    from services.llm import generate


def analyze_recovery(repository_data, *, evidence_pack=None, live=False):
    """Project Recovery — health check and practical next steps."""
    if evidence_pack is not None:
        if live:
            from backend.services.llm import structured_prediction
            return structured_prediction("recovery", evidence_pack, specialized=True)
        return {
            "score": None,
            "confidence": "LOW",
            "claims": [],
            "analysis_mode": (
                "local abstention; current recovery agent has no calibrated numeric ranking"
            ),
        }

    if os.getenv("USE_GEMINI_ANALYSIS", "false").lower() != "true":
        summary = repository_data.get("repository_summary", repository_data)
        commits = summary.get("total_commits", summary.get("commit_count", 0))
        todos = summary.get("todo_count", len(summary.get("todos", [])))
        return (
            "Local recovery assessment:\n"
            f"- Observed commits: {commits}\n"
            f"- Observed TODO/FIXME markers: {todos}\n"
            "- Recovery potential: MEDIUM\n"
            "- Recommendation: REVIEW — add tests and confirm deployment configuration.\n"
            "Set USE_GEMINI_ANALYSIS=true and GEMINI_API_KEY for full online Project Recovery Analysis."
        )

    # Online path (Gemini)
    prompt = f"""
You are the Project Recovery agent in an Agentic AI Framework for software repositories.

Your job: judge whether this repository is practical to continue, and give clear recovery advice.

REPOSITORY EVIDENCE:
{repository_data}

Produce a structured assessment with:

1. Possible cause of drift or abandonment (if any)
2. Current completion status (early / mid / late / unclear) with brief justification
3. Remaining work (concrete items: TODOs, tests, docs, deployment, etc.)
4. Recovery potential: HIGH | MEDIUM | LOW
5. Recommendation: CONTINUE | REVIEW | NOT_RECOMMENDED
6. Practical next steps (3–5 bullet points a developer or manager can act on)
7. Confidence: HIGH | MEDIUM | LOW

Rules:
- Use only the evidence provided (commits, TODOs, summaries, recent activity).
- Do not invent stars, users, or external popularity.
- Activity alone does not mean the project is healthy; TODOs and gaps matter.
- If evidence is weak, say so and lower confidence.
"""

    return generate(prompt)
