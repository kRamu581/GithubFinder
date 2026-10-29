import os

try:
    from backend.services.llm import generate
except ModuleNotFoundError:
    from services.llm import generate


def analyze_scope(
    task_description,
    changed_files,
    *,
    evidence_pack=None,
    live=False,
    commit=None,
):
    """Scope Creep Detection — compare planned task vs actual code changes."""
    if evidence_pack is not None:
        if live:
            from backend.services.llm import structured_prediction
            return structured_prediction("scope", evidence_pack, specialized=True)
        return {
            "hunks": {h["id"]: "unclear" for h in evidence_pack.get("hunks", [])},
            "verdict": "justify",
            "confidence": "LOW",
            "claims": [],
            "analysis_mode": "local abstention; semantic scope requires review",
        }

    if os.getenv("USE_GEMINI_ANALYSIS", "false").lower() != "true":
        return (
            "Verdict: INSUFFICIENT_EVIDENCE\n"
            f"Requested task: {task_description}\n"
            f"Changed files: {', '.join(changed_files or [])}\n"
            "Local analysis cannot determine semantic relevance. "
            "Set USE_GEMINI_ANALYSIS=true and GEMINI_API_KEY for online Scope Creep Detection."
        )

    diff_section = ""
    if commit and commit.get("diff"):
        diff_section = f"\nACTUAL CODE DIFFS:\n{commit.get('diff')}\n"

    # Online path (Gemini)
    prompt = f"""
You are the Scope Creep Detection agent in an Agentic AI Framework for software projects.

Your job: decide whether the developer's code changes stayed within the planned task, or went beyond it (scope creep).

PLANNED TASK / GOAL:
{task_description}

FILES THE DEVELOPER CHANGED:
{changed_files}
{diff_section}
Analyze whether each change supports the planned task or looks unrelated / extra.

Return a clear text report with these sections:

1. Verdict: IN_SCOPE | POSSIBLE_SCOPE_CREEP | CLEAR_SCOPE_CREEP | INSUFFICIENT_EVIDENCE
2. Related changes (files or edits that match the task)
3. Unrelated or suspicious changes (possible creep)
4. Short explanation (2–4 sentences)
5. Confidence: HIGH | MEDIUM | LOW

Rules:
- Base the verdict on the task vs files/diffs only.
- Do not invent files or requirements that were not provided.
- If the task is vague and diffs are limited, use INSUFFICIENT_EVIDENCE.
- Supporting refactors next to a feature can still be IN_SCOPE if they clearly serve the task.
"""

    return generate(prompt)
