from fastapi import FastAPI, Query, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


@app.get("/issues/by-category-location")
def get_issues_by_category_location(
    issue_category: str = Query(...),
    issue_location: str = Query(...)
):

    try:
        response = (
            supabase
            .from_("issues")
            .select(
                """
                issue_id,
                issue_category,
                issue_weight,
                estimated_cost_range,
                created_at,
                issue_reports!inner(
                    report_id,
                    issue_description,
                    reported_by_name,
                    reported_by_phone,
                    reported_on,
                    evidence,
                    issue_location,
                    latitude,
                    longitude
                )
                """
            )
            .ilike("issue_category", issue_category)
            .ilike("issue_reports.issue_location", issue_location)
            .order("created_at", desc=True)
            .execute()
        )

        data = response.data or []

        issues = []

        for item in data:
            reports = item.get("issue_reports", [])

            for report in reports:
                issues.append({
                    "issue_id": item["issue_id"],
                    "issue_category": item["issue_category"],
                    "issue_weight": item["issue_weight"],
                    "estimated_cost_range": item["estimated_cost_range"],
                    "created_at": item["created_at"],

                    "report_id": report["report_id"],
                    "issue_description": report["issue_description"],
                    "reported_by_name": report["reported_by_name"],
                    "reported_by_phone": report["reported_by_phone"],
                    "reported_on": report["reported_on"],
                    "evidence": report["evidence"],
                    "issue_location": report["issue_location"],
                    "latitude": report["latitude"],
                    "longitude": report["longitude"]
                })

        return {
            "issue_category": issue_category,
            "issue_location": issue_location,
            "total_issues": len(issues),
            "issues": issues
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch issues: {str(e)}"
        )

@app.get("/issue-report/{report_id}")
def get_issue_report(report_id: int):

    try:
        response = (
            supabase
            .from_("issue_reports")
            .select(
                """
                report_id,
                issue_id,
                issue_description,
                reported_by_name,
                reported_by_phone,
                reported_on,
                evidence,
                issue_location,
                latitude,
                longitude,
                issues(
                    issue_id,
                    issue_category,
                    issue_weight,
                    estimated_cost_range,
                    created_at,
                    ward_processed,
                    ward_processed_at
                )
                """
            )
            .eq("report_id", report_id)
            .maybe_single()
            .execute()
        )

        data = response.data

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"Report with report_id {report_id} not found"
            )

        issue_data = data.get("issues")

        return {
            "report_id": data.get("report_id"),
            "issue_id": data.get("issue_id"),

            "issue_category": (
                issue_data.get("issue_category")
                if issue_data
                else None
            ),

            "issue_weight": (
                issue_data.get("issue_weight")
                if issue_data
                else None
            ),

            "estimated_cost_range": (
                issue_data.get("estimated_cost_range")
                if issue_data
                else None
            ),

            "issue_description": data.get("issue_description"),

            "reported_by_name": data.get("reported_by_name"),
            "reported_by_phone": data.get("reported_by_phone"),
            "reported_on": data.get("reported_on"),

            "evidence": data.get("evidence"),

            "issue_location": data.get("issue_location"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),

            "issue_created_at": (
                issue_data.get("created_at")
                if issue_data
                else None
            ),

            "ward_processed": (
                issue_data.get("ward_processed")
                if issue_data
                else None
            ),

            "ward_processed_at": (
                issue_data.get("ward_processed_at")
                if issue_data
                else None
            )
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch report: {str(e)}"
        )