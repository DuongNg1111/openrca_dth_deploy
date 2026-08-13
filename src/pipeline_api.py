from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Thread
import traceback

from contextlib import redirect_stdout
from pathlib import Path
import io

from src.full_pipeline import run_pipeline


app = FastAPI(
    title="OpenRCA Pipeline API"
)


class PipelineRequest(BaseModel):
    issue_key: str


# =====================================================
# TEMPORARY PRESENTATION SETTING
# =====================================================
# Chỉ issue này mới được lưu pipeline output ra TXT.
#
# Ví dụ:
# SAVE_OUTPUT_ISSUE = "DEV-205"
#
# Sau khi quay/chụp evidence xong:
# SAVE_OUTPUT_ISSUE = None
#
# Các issue khác vẫn chạy pipeline bình thường.
# =====================================================

SAVE_OUTPUT_ISSUE = "DEV-220"


def run_pipeline_background(issue_key: str):

    try:

        print(
            f"\nStarting RCA pipeline for {issue_key}"
        )

        # =================================================
        # NORMAL PIPELINE
        # =================================================
        # Các ticket KHÁC với SAVE_OUTPUT_ISSUE
        # sẽ chạy bình thường và KHÔNG tạo file TXT.
        # =================================================

        if issue_key != SAVE_OUTPUT_ISSUE:

            result = run_pipeline(
                issue_key,
                run_agents=True,
                dry_run=False
            )

        # =================================================
        # TEMPORARY PRESENTATION LOGGING
        # =================================================
        # Chỉ ticket được chỉ định mới capture output.
        # =================================================

        else:

            output_file = Path(
                f"pipeline_output_{issue_key}.txt"
            )

            buffer = io.StringIO()

            print(
                f"\nCapturing pipeline output for "
                f"{issue_key}"
            )

            # Capture toàn bộ print() từ full_pipeline.py
            with redirect_stdout(buffer):

                result = run_pipeline(
                    issue_key,
                    run_agents=True,
                    dry_run=False
                )

            # Lấy toàn bộ output Step 1 → Step 22
            pipeline_output = buffer.getvalue()

            # Lưu ra file TXT
            output_file.write_text(
                pipeline_output,
                encoding="utf-8"
            )

            # In lại terminal để vẫn xem được output
            print(
                pipeline_output
            )

            print(
                f"\nPipeline output saved to: "
                f"{output_file}"
            )

        # =================================================
        # PIPELINE COMPLETED
        # =================================================

        print(
            f"\nRCA pipeline completed for {issue_key}"
        )

        print(result)

    except Exception as e:

        # =================================================
        # PIPELINE FAILED
        # =================================================

        print(
            f"\nRCA pipeline failed for {issue_key}"
        )

        print(e)

        traceback.print_exc()


# =====================================================
# TRIGGER PIPELINE
# =====================================================

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

    # =================================================
    # RUN PIPELINE IN BACKGROUND
    # =================================================

    thread = Thread(
        target=run_pipeline_background,
        args=(issue_key,),
        daemon=True
    )

    thread.start()

    # =================================================
    # RETURN IMMEDIATELY TO STREAMLIT
    # =================================================

    return {
        "success": True,
        "issue_key": issue_key,
        "status": "Processing"
    }