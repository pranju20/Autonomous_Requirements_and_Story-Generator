class HumanApprovalAgent:
    """
    HITL is handled via FastAPI endpoints in main.py:
      POST /approve/{run_id}  → human approves, gherkin runs
      POST /reject/{run_id}   → human rejects with feedback

    This node just prints a summary and marks the pipeline
    ready for the API to pause on.
    """

    def run(self, state):
        reqs = state["requirements"]

        print("\n=== REQUIREMENTS FOR REVIEW ===")
        for i, r in enumerate(reqs, 1):
            title = r["title"] if isinstance(r, dict) else r.title
            desc = r["description"] if isinstance(r, dict) else r.description
            print(f"  {i}. [{title}] {desc}")

        print("\n⏸  Pipeline paused — waiting for human approval via API")
        print("   → POST /approve/{run_id}  to proceed")
        print("   → POST /reject/{run_id}   to reject\n")

        state["hitl_status"] = "pending"
        return state
