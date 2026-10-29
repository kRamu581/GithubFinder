import os

try:
    from backend.services.llm import generate
except ModuleNotFoundError:
    from services.llm import generate


def generate_final_report(
    repository_summary,
    intent_analysis,
    scope_analysis,
    recovery_analysis,
):
    """Unified report combining Intent, Scope Creep, and Recovery."""
    if os.getenv("USE_GEMINI_ANALYSIS", "false").lower() != "true":
        return (
            "Overall repository condition: Review recommended.\n\n"
            f"Repository summary: {repository_summary}\n\n"
            f"Intent findings: {intent_analysis}\n\n"
            f"Scope findings: {scope_analysis}\n\n"
            f"Recovery findings: {recovery_analysis}\n\n"
            "Next action: set USE_GEMINI_ANALYSIS=true with GEMINI_API_KEY "
            "for a full online multi-agent report."
        )

    prompt = f"""
You are the Final Report agent in an Agentic AI Framework with three core capabilities:
1) Code Intent Analysis
2) Scope Creep Detection
3) Software Project Recovery

Combine the agent outputs into one clear report for a developer or project manager.

Repository Summary:
{repository_summary}

Intent Analysis:
{intent_analysis}

Scope Analysis:
{scope_analysis}

Recovery Analysis:
{recovery_analysis}

Write a structured report with:

1. Overall repository condition (1–2 sentences)
2. Code Intent — main finding
3. Scope Creep — main finding (or note if skipped / insufficient task)
4. Project Recovery — main finding and recommendation
5. Important risks
6. Recommended next actions (bullets)
7. Final recommendation

Be evidence-based. Do not invent facts. If any agent lacked evidence, say so clearly.
"""

    return generate(prompt)
