import os

try:
    from backend.services.llm import generate
except ModuleNotFoundError:
    from services.llm import generate


def analyze_intent(commit, file_histories, evidence_map, *, evidence_pack=None, live=False):
    """Code Intent Analysis — reconstruct WHY a change exists."""
    if evidence_pack is not None:
        if live:
            from backend.services.llm import structured_prediction
            return structured_prediction("intent", evidence_pack, specialized=True)
        message = commit.get("message", "")
        return {
            "intent": message,
            "introducing_commit": None,
            "confidence": "LOW",
            "analysis_mode": "local fallback; introducing region not inferred",
            "claims": [{
                "text": message,
                "quote": message,
                "kind": "quote",
                "commit": commit.get("hash"),
                "file": None,
                "hunk": None,
            }],
        }

    if os.getenv("USE_GEMINI_ANALYSIS", "false").lower() != "true":
        changed_files = commit.get("changed_files", [])
        return {
            "likely_intent": commit.get("message", "No commit message available."),
            "code_change_summary": (
                f"The commit changes {len(changed_files)} file(s): "
                + ", ".join(changed_files[:5])
            ),
            "historical_context": (
                f"{len(file_histories)} changed file(s) have available history."
            ),
            "confidence": "LOW",
            "evidence": [{
                "type": "commit",
                "reference": commit.get("hash", "unknown"),
                "reason": "Derived from the commit message and changed-file list.",
            }],
            "analysis_mode": (
                "local fallback — set USE_GEMINI_ANALYSIS=true and GEMINI_API_KEY "
                "for full online Code Intent Analysis"
            ),
        }

    # Online path (Gemini)
    prompt = f"""
You are the Code Intent Analysis agent in an Agentic AI Framework for software repositories.

Your job: reconstruct the REAL reason this code change exists, using evidence — not only the commit message.

COMMIT HASH:
{commit.get("hash")}

COMMIT MESSAGE:
{commit.get("message")}

CHANGED FILES:
{commit.get("changed_files")}

ACTUAL CODE DIFF (patches):
{commit.get("diff", [])}

FILE HISTORY (introduction and recent changes):
{file_histories}

EVIDENCE MAP:
{evidence_map}

Return ONLY valid JSON:
{{
    "likely_intent": "One clear sentence: why this change was made",
    "code_change_summary": "What was added, modified, or removed (based on diffs/files)",
    "historical_context": "How this relates to earlier history of these files, if known",
    "confidence": "HIGH | MEDIUM | LOW",
    "evidence": [
        {{
            "type": "commit | file | diff | history",
            "reference": "hash, path, or short id",
            "reason": "Why this supports the intent conclusion"
        }}
    ]
}}

Rules:
- Prefer diff and history evidence over the commit message alone.
- Do not invent developer motives that have no support in the evidence.
- If the message is vague but diffs are clear, say so and base intent on the diffs.
- Use LOW confidence when evidence is thin.
"""

    return generate(prompt, structured=True)
