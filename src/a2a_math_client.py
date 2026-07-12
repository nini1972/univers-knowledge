"""
A2A Math Service Client — Temporary integration test module.

Calls the Cloud Run Math Agent's /a2a/task endpoint to verify that
the AstralBridge A2A protocol works end-to-end in a real workflow run.

This module is intentionally lightweight and non-blocking:
- If the service is unreachable, it returns None and logs a warning.
- If the response is malformed, it returns None and logs a warning.
"""

import os
import re
import json
import urllib.request
import urllib.error


# Default to the known Cloud Run URL; can be overridden via env var.
_DEFAULT_URL = "https://math-agent-907993744320.us-central1.run.app"
_TIMEOUT_SECONDS = 30


def extract_equations_from_report(math_report: str) -> list[str]:
    """Extract LaTeX equations from a math verification report.

    Looks for display math ($$...$$) and inline math ($...$) patterns.
    Returns a list of equation strings, or a fallback if none found.
    """
    if not math_report:
        return []

    # Extract display math first ($$...$$)
    display_eqs = re.findall(r'\$\$(.+?)\$\$', math_report, re.DOTALL)
    # Then inline math ($...$), avoiding already-matched display math
    inline_eqs = re.findall(r'(?<!\$)\$([^$]+?)\$(?!\$)', math_report)

    equations = [eq.strip() for eq in display_eqs + inline_eqs if eq.strip()]

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for eq in equations:
        if eq not in seen:
            seen.add(eq)
            unique.append(eq)

    return unique


def call_a2a_math_service(concept: str, equations: list[str]) -> dict | None:
    """Call the A2A Math Service endpoint.

    Args:
        concept: The physics concept being verified.
        equations: List of LaTeX equation strings to verify.

    Returns:
        The task result dict on success, or None on failure.
    """
    base_url = (os.getenv("MATH_SERVICE_URL") or _DEFAULT_URL).rstrip("/")
    endpoint = f"{base_url}/a2a/task"

    payload = {
        "capability": "verify_derivation",
        "payload": {
            "concept": concept,
            "equations": equations if equations else ["E = mc^2"]  # Fallback test equation
        }
    }

    print(f"[A2A MATH TEST] Calling Math Service at {endpoint}")
    print(f"[A2A MATH TEST] Payload: concept={concept!r}, equations={len(equations)} found")

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            response_body = resp.read().decode("utf-8")
            result = json.loads(response_body)

        task_id = result.get("id", "unknown")
        status = result.get("status", "unknown")
        print(f"[A2A MATH TEST] ✅ Response: task_id={task_id}, status={status}")

        if result.get("result", {}).get("proof_report"):
            report_preview = result["result"]["proof_report"][:200]
            print(f"[A2A MATH TEST] Proof report preview: {report_preview}...")

        return result

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        print(f"[A2A MATH TEST] ⚠️ HTTP {e.code} from Math Service: {body}")
        return None

    except urllib.error.URLError as e:
        print(f"[A2A MATH TEST] ⚠️ Connection failed: {e.reason}")
        return None

    except Exception as e:
        print(f"[A2A MATH TEST] ⚠️ Unexpected error: {e}")
        return None
