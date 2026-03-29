# import uuid
# from fastapi import FastAPI, HTTPException
# from models.schemas import InputRequest, OutputResponse, WorkflowState
# from workflow.graph import build_graph

# app = FastAPI(title="Autonomous Requirements & Story Generator")
# graph = build_graph()

# # In-memory store for pending runs (use Redis in production)
# pending_runs: dict[str, dict] = {}


# @app.post("/process")
# def process(request: InputRequest):
#     """
#     Step 1 — Start the pipeline.
#     Runs: input → extract → dedup → conflict → acceptance_criteria
#     Then PAUSES and returns run_id for human review.
#     """
#     run_id = str(uuid.uuid4())[:8]

#     initial_state: WorkflowState = {
#         "raw_input": request.input_text,
#         "cleaned_input": "",
#         "requirements": [],
#         "conflicts": [],
#         "approved": False,
#         "gherkin_output": [],
#         "run_id": run_id,
#         "hitl_status": "pending",
#     }

#     try:
#         result = graph.invoke(initial_state)

#         # Store state — waiting for human approval
#         pending_runs[run_id] = result

#         reqs = result["requirements"]
#         conflicts = result["conflicts"]

#         print(f"\n{'='*50}")
#         print(f"Run {run_id} PAUSED — waiting for human approval")
#         print(f"Requirements found: {len(reqs)}")
#         print(f"Conflicts found:    {len(conflicts)}")
#         print(f"Call POST /approve/{run_id} or POST /reject/{run_id}")
#         print(f"{'='*50}\n")

#         return {
#             "run_id": run_id,
#             "status": "pending_approval",
#             "message": f"Review requirements below, then POST to /approve/{run_id} or /reject/{run_id}",
#             "requirements": reqs,
#             "conflicts": conflicts,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/approve/{run_id}", response_model=OutputResponse)
# def approve(run_id: str):
#     """
#     Step 2a — Human approves. Runs gherkin generation and returns final output.
#     """
#     if run_id not in pending_runs:
#         raise HTTPException(
#             status_code=404, detail=f"Run '{run_id}' not found or already completed."
#         )

#     state = pending_runs.pop(run_id)
#     state["approved"] = True
#     state["hitl_status"] = "approved"

#     print(f"\n✅ Run {run_id} APPROVED — running Gherkin generation...")

#     try:
#         # Run only the gherkin node on the approved state
#         from agents.gherkin_test_generator import GherkinTestGeneratorAgent

#         state = GherkinTestGeneratorAgent().run(state)

#         return OutputResponse(
#             requirements=state["requirements"],
#             conflicts=state["conflicts"],
#             approved=state["approved"],
#             gherkin_output=state["gherkin_output"],
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/reject/{run_id}")
# def reject(run_id: str, feedback: str = "No feedback provided"):
#     """
#     Step 2b — Human rejects. Clears the run and returns feedback.
#     """
#     if run_id not in pending_runs:
#         raise HTTPException(
#             status_code=404, detail=f"Run '{run_id}' not found or already completed."
#         )

#     pending_runs.pop(run_id)
#     print(f"\n❌ Run {run_id} REJECTED — feedback: {feedback}")

#     return {
#         "run_id": run_id,
#         "status": "rejected",
#         "feedback": feedback,
#         "message": "Run rejected. Submit new input via POST /process to restart.",
#     }


# @app.get("/status/{run_id}")
# def status(run_id: str):
#     """Check if a run is still pending approval."""
#     if run_id not in pending_runs:
#         return {"run_id": run_id, "status": "not_found_or_completed"}
#     state = pending_runs[run_id]
#     return {
#         "run_id": run_id,
#         "status": "pending_approval",
#         "requirements_count": len(state["requirements"]),
#         "conflicts_count": len(state["conflicts"]),
#         "requirements": state["requirements"],
#     }


# @app.get("/health")
# def health():
#     return {"status": "ok", "pending_runs": len(pending_runs)}
"""
api/main.py  —  UPGRADED: saves approved requirements into RAG vector store

After human approves, requirements are embedded and stored in FAISS.
On the next run, similar requirements are retrieved and injected into
the extraction prompt — preventing duplicates across runs.
"""

import uuid
from fastapi import FastAPI, HTTPException
from models.schemas import InputRequest, OutputResponse, WorkflowState
from workflow.graph import build_graph
from rag.vector_store import vector_store

app = FastAPI(title="Autonomous Requirements & Story Generator")
graph = build_graph()

pending_runs: dict[str, dict] = {}


@app.post("/process")
def process(request: InputRequest):
    """
    Step 1 — Run pipeline up to HITL gate.
    Returns run_id and extracted requirements for human review.
    """
    run_id = str(uuid.uuid4())[:8]

    initial_state: WorkflowState = {
        "raw_input": request.input_text,
        "cleaned_input": "",
        "requirements": [],
        "conflicts": [],
        "approved": False,
        "gherkin_output": [],
        "run_id": run_id,
        "hitl_status": "pending",
    }

    try:
        result = graph.invoke(initial_state)
        pending_runs[run_id] = result

        reqs = result["requirements"]
        conflicts = result["conflicts"]

        print(f"\n{'='*50}")
        print(f"Run {run_id} PAUSED — waiting for human approval")
        print(f"Requirements found: {len(reqs)}")
        print(f"Conflicts found:    {len(conflicts)}")
        print(f"→ POST /approve/{run_id}  to proceed")
        print(f"→ POST /reject/{run_id}   to reject")
        print(f"{'='*50}\n")

        return {
            "run_id": run_id,
            "status": "pending_approval",
            "message": f"Review below, then POST to /approve/{run_id} or /reject/{run_id}",
            "requirements": reqs,
            "conflicts": conflicts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve/{run_id}", response_model=OutputResponse)
def approve(run_id: str):
    """
    Step 2a — Human approves.
    Runs Gherkin generation, then saves requirements to RAG vector store.
    """
    if run_id not in pending_runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    state = pending_runs.pop(run_id)
    state["approved"] = True
    state["hitl_status"] = "approved"

    print(f"\n✅ Run {run_id} APPROVED — generating Gherkin tests...")

    try:
        from agents.gherkin_test_generator import GherkinTestGeneratorAgent

        state = GherkinTestGeneratorAgent().run(state)

        # ── RAG: store approved requirements for future runs ──────────────
        reqs = state["requirements"]
        if reqs:
            vector_store.add(reqs)
            print(
                f"[RAG] {len(reqs)} requirements saved to vector store for future RAG retrieval."
            )

        return OutputResponse(
            requirements=state["requirements"],
            conflicts=state["conflicts"],
            approved=state["approved"],
            gherkin_output=state["gherkin_output"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reject/{run_id}")
def reject(run_id: str, feedback: str = "No feedback provided"):
    """Step 2b — Human rejects. Requirements are NOT saved to RAG."""
    if run_id not in pending_runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    pending_runs.pop(run_id)
    print(f"\n❌ Run {run_id} REJECTED — feedback: {feedback}")

    return {
        "run_id": run_id,
        "status": "rejected",
        "feedback": feedback,
        "message": "Run rejected. POST to /process to restart.",
    }


@app.get("/status/{run_id}")
def status(run_id: str):
    """Check pending run status and preview requirements."""
    if run_id not in pending_runs:
        return {"run_id": run_id, "status": "not_found_or_completed"}
    state = pending_runs[run_id]
    return {
        "run_id": run_id,
        "status": "pending_approval",
        "requirements_count": len(state["requirements"]),
        "conflicts_count": len(state["conflicts"]),
        "requirements": state["requirements"],
    }


@app.get("/rag/memory")
def rag_memory():
    """View how many requirements are stored in RAG memory."""
    return {
        "total_stored": vector_store.index.ntotal,
        "documents": vector_store.documents,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "pending_runs": len(pending_runs),
        "rag_memory": vector_store.index.ntotal,
    }
