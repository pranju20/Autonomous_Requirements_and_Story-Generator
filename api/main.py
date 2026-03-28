from fastapi import FastAPI, HTTPException
from workflow.graph import build_graph
from models.schemas import WorkflowState, InputRequest, OutputResponse

app = FastAPI()
graph = build_graph()


@app.post("/process", response_model=OutputResponse)
def process(request: InputRequest):
    try:
        state = WorkflowState(raw_input=request.input_text)
        result = graph.invoke(state)
        if isinstance(result, dict):
            state = WorkflowState(**result)
        else:
            state = result
        return OutputResponse(
            requirements=result.requirements,
            conflicts=result.conflicts,
            approved=result.approved,
            gherkin_output=result.gherkin_output,
        )

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
