"""
Aggregates LLM-judge scores and applies the production-readiness gate:
a simple pass/fail threshold check before the twin is considered
ready to "ship".
"""
import json

THRESHOLDS = {
    "style_fidelity": 3.5,
    "factual_grounding": 4.0,
    "coherence": 4.0,
}


def aggregate(results_path: str = "evaluation/eval_results.json") -> dict:
    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    scored = [r for r in results if r.get("style_fidelity") is not None]
    if not scored:
        return {"pass": False, "reason": "no scored examples"}

    averages = {
        dim: sum(r[dim] for r in scored) / len(scored)
        for dim in ["style_fidelity", "factual_grounding", "coherence"]
    }

    gate_pass = all(averages[dim] >= THRESHOLDS[dim] for dim in THRESHOLDS)

    return {"pass": gate_pass, "averages": averages, "thresholds": THRESHOLDS, "n_examples": len(scored)}


if __name__ == "__main__":
    report = aggregate()
    print(json.dumps(report, indent=2))
    if report["pass"]:
        print("[metrics] PRODUCTION READINESS GATE: PASS")
    else:
        print("[metrics] PRODUCTION READINESS GATE: FAIL")
