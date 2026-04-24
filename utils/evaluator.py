def evaluate_output(output: str) -> dict:
    """
    Simple heuristic evaluation
    """

    score = 0

    if output and len(output) > 50:
        score += 1

    if "ERROR" not in output:
        score += 1

    if "-" in output or "•" in output:
        score += 1

    return {
        "score": score,
        "valid": score >= 2
    }