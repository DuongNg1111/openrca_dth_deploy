from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Thread

from src.full_pipeline import run_pipeline


app = FastAPI(
    title="OpenRCA Pipeline API"
)


class PipelineRequest(BaseModel):
    issue_key: str


def run_pipeline_background(issue_key: str):

    try:

        print(
            f"\nStarting RCA pipeline for {issue_key}"
        )

        result = run_pipeline(
            issue_key,
            run_agents=True
        )

        print(
            f"\nRCA pipeline completed for {issue_key}"
        )

        print(result)

    except Exception as e:

        print(
            f"\nRCA pipeline failed for {issue_key}"
        )

        print(e)


@app.post("/run-pipeline")
def trigger_pipeline(
    request: PipelineRequest
):

    issue_key = request.issue_key.strip()

    if not issue_key:

        raise HTTPException(
            status_code=400,
            detail="issue_key is required"
        )

    thread = Thread(
        target=run_pipeline_background,
        args=(issue_key,),
        daemon=True
    )

    thread.start()

    return {
        "success": True,
        "issue_key": issue_key,
        "status": "Processing"
    }