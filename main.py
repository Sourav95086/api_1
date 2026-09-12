from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/report-id")
def get_report_id(issue_id: int):
    try:
        response = (
            supabase
            .table("issue_reports")
            .select("reportId")
            .eq("issueId", issue_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for issue id {issue_id}"
            )

        return {
            "issue_id": issue_id,
            "report_id": response.data[0]["reportId"]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )