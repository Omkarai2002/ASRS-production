"""
Backend helpers package
Reusable utilities and database operations
"""

from .db_queries import (
    get_user_reports,
    get_report_by_id,
    get_report_count_for_user,
    get_inferences_by_report,
    search_inferences,
    search_inferences_by_vin,
    search_inferences_by_unique_id,
    get_inference_count_by_exclusion,
    get_daily_statistics,
    get_total_statistics,
    get_user_settings,
    create_or_update_user_settings,
    batch_delete_inferences,
    get_inference_with_details,
)

__all__ = [
    "get_user_reports",
    "get_report_by_id",
    "get_report_count_for_user",
    "get_inferences_by_report",
    "search_inferences",
    "search_inferences_by_vin",
    "search_inferences_by_unique_id",
    "get_inference_count_by_exclusion",
    "get_daily_statistics",
    "get_total_statistics",
    "get_user_settings",
    "create_or_update_user_settings",
    "batch_delete_inferences",
    "get_inference_with_details",
]
