"""
File Review API endpoints
AI-powered file analysis and issue detection
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.gemini_service import get_gemini_service
from app.services.file_storage import get_file_storage
from app.services.csv_validator import get_csv_validator

router = APIRouter()


class ReviewFileRequest(BaseModel):
    """Request model for file review"""
    file_id: str
    entity_name: str
    include_suggestions: bool = True


class ReviewResponse(BaseModel):
    """Response model for file review"""
    file_id: str
    entity_name: str
    issues_found: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    can_auto_fix: bool
    summary: str
    total_issues: int
    critical_issues: int
    warnings: int


@router.post("/review/file", response_model=ReviewResponse)
async def review_file(request: ReviewFileRequest):
    """
    Review uploaded file for issues and suggest fixes

    Uses AI to analyze the file and detect:
    - Missing required fields
    - Misspelled or misnamed columns
    - Data quality issues
    - Format errors
    - Suggested corrections

    Args:
        request: ReviewFileRequest with file_id and entity_name

    Returns:
        ReviewResponse with detected issues and suggestions

    Raises:
        400: Invalid request
        404: File not found
        500: Error during review
    """
    if not request.file_id or not request.entity_name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "file_id and entity_name are required"
                },
                "status": 400
            }
        )

    # Get file data
    try:
        storage = get_file_storage()
        print(f"[DEBUG] Looking for file_id: {request.file_id}")
        print(f"[DEBUG] Storage metadata keys: {list(storage._metadata.keys())}")

        df = storage.get_dataframe(request.file_id)

        if df is None:
            print(f"[DEBUG] DataFrame is None for file_id: {request.file_id}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": f"File with ID {request.file_id} not found in storage"
                    },
                    "status": 404
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] Exception getting file: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": f"Error retrieving file: {str(e)}"
                },
                "status": 500
            }
        )

    # Extract file info
    source_fields = df.columns.tolist()
    sample_data = df.head(5).to_dict('records')

    # Get metadata for filename
    metadata = storage.get_metadata(request.file_id)
    filename = metadata.get("original_filename", "uploaded_file.csv") if metadata else "uploaded_file.csv"

    # Step 1: Schema-based validation (fast, deterministic)
    validator = get_csv_validator()
    is_valid, validation_issues = validator.validate_file(
        df=df,
        entity_name=request.entity_name,
        filename=filename
    )

    # Convert validation issues to dict format
    schema_issues = [issue.to_dict() for issue in validation_issues]
    print(f"[DEBUG] Validation completed: is_valid={is_valid}, issues_count={len(validation_issues)}")
    print(f"[DEBUG] Schema issues: {schema_issues}")

    # Step 2: AI-powered analysis (context-aware)
    ai_issues = []
    ai_suggestions = []
    can_auto_fix = False
    summary = ""

    try:
        gemini_service = get_gemini_service()
        analysis = await gemini_service.analyze_file_issues(
            source_fields=source_fields,
            sample_data=sample_data,
            entity_name=request.entity_name
        )

        ai_issues = analysis.get("issues_found", [])
        ai_suggestions = analysis.get("suggestions", [])
        can_auto_fix = analysis.get("can_auto_fix", False)
        summary = analysis.get("summary", "")
    except Exception as e:
        print(f"[WARNING] AI analysis failed: {str(e)}")
        # Continue with schema validation results only
        summary = f"Schema validation completed. AI analysis unavailable: {str(e)}"

    # Step 3: Combine results (schema validation takes priority)
    # Deduplicate issues based on field name and type
    seen_issues = set()
    combined_issues = []

    # Add schema validation issues first (they're more accurate)
    for issue in schema_issues:
        key = (issue.get("field", ""), issue.get("type", ""))
        if key not in seen_issues:
            seen_issues.add(key)
            combined_issues.append(issue)

    # Add AI issues that aren't duplicates
    for issue in ai_issues:
        key = (issue.get("field", ""), issue.get("type", ""))
        if key not in seen_issues:
            seen_issues.add(key)
            combined_issues.append(issue)

    # Combine suggestions (schema suggestions first)
    schema_suggestions = [
        {
            "issue_type": issue.get("type", ""),
            "field": issue.get("field", ""),
            "suggestion": issue.get("suggestion", ""),
            "auto_fixable": issue.get("type") == "misspelled_header",
            "target_field": issue.get("suggestion", "").split("'")[-2] if issue.get("suggestion") and "'" in issue.get("suggestion", "") else None
        }
        for issue in schema_issues
        if issue.get("suggestion")
    ]

    combined_suggestions = schema_suggestions + ai_suggestions

    # Update summary if we have validation issues
    if not summary and validation_issues:
        summary = f"Found {len(validation_issues)} validation issue(s). "
        if not is_valid:
            summary += "Critical issues must be fixed before proceeding."
        else:
            summary += "Review warnings and suggestions."
    elif not summary:
        summary = "No issues found. File looks good!"

    # Count issues by severity
    critical_issues = sum(
        1 for issue in combined_issues
        if issue.get("severity") == "critical"
    )
    warnings = sum(
        1 for issue in combined_issues
        if issue.get("severity") == "warning"
    )

    return ReviewResponse(
        file_id=request.file_id,
        entity_name=request.entity_name,
        issues_found=combined_issues,
        suggestions=combined_suggestions,
        can_auto_fix=can_auto_fix,
        summary=summary,
        total_issues=len(combined_issues),
        critical_issues=critical_issues,
        warnings=warnings
    )


@router.post("/review/apply-fixes")
async def apply_auto_fixes(request: ReviewFileRequest):
    """
    Apply auto-fixes to the uploaded file

    Applies AI-suggested corrections to the file data

    Args:
        request: ReviewFileRequest with file_id and entity_name

    Returns:
        Result with updated file information

    Raises:
        400: Invalid request
        404: File not found
        500: Error applying fixes
    """
    # Get file and review results
    storage = get_file_storage()
    df = storage.get_dataframe(request.file_id)

    if df is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": f"File with ID {request.file_id} not found"
                },
                "status": 404
            }
        )

    # Get AI suggestions
    gemini_service = get_gemini_service()
    source_fields = df.columns.tolist()
    sample_data = df.head(5).to_dict('records')

    analysis = await gemini_service.analyze_file_issues(
        source_fields=source_fields,
        sample_data=sample_data,
        entity_name=request.entity_name
    )

    # Apply fixes
    fixes_applied = []
    errors = []

    for suggestion in analysis.get("suggestions", []):
        if suggestion.get("auto_fixable", False):
            try:
                # Apply the fix based on suggestion type
                if suggestion["issue_type"] == "misspelled_field":
                    old_name = suggestion["field"]
                    new_name = suggestion["target_field"]

                    if old_name in df.columns:
                        df.rename(columns={old_name: new_name}, inplace=True)
                        fixes_applied.append({
                            "type": "rename_column",
                            "from": old_name,
                            "to": new_name
                        })

                # Add more fix types here as needed

            except Exception as e:
                errors.append({
                    "suggestion": suggestion,
                    "error": str(e)
                })

    # Store updated DataFrame
    if fixes_applied:
        new_file_id = storage.store_dataframe(df, f"fixed_{request.file_id}")

        return {
            "success": True,
            "original_file_id": request.file_id,
            "fixed_file_id": new_file_id,
            "fixes_applied": fixes_applied,
            "fixes_count": len(fixes_applied),
            "errors": errors
        }
    else:
        return {
            "success": False,
            "message": "No auto-fixable issues found",
            "errors": errors
        }


@router.post("/review/suggest-mapping")
async def suggest_field_mapping_ai(
    source_field: str,
    entity_name: str,
    context: List[str] = None
):
    """
    Get AI-powered field mapping suggestions

    Args:
        source_field: Source field to map
        entity_name: Target entity type
        context: Other source field names for context

    Returns:
        List of mapping suggestions with confidence scores
    """
    try:
        gemini_service = get_gemini_service()
        suggestions = await gemini_service.suggest_field_mapping(
            source_field=source_field,
            entity_name=entity_name,
            context=context
        )

        return {
            "source_field": source_field,
            "entity_name": entity_name,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SUGGESTION_ERROR",
                    "message": f"Error getting suggestions: {str(e)}"
                },
                "status": 500
            }
        )
