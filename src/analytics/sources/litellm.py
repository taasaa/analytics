"""LiteLLM data source - PostgreSQL queries and data models"""

from datetime import datetime
from typing import List, Dict, Any
from analytics.db import Database


def get_requests(db: Database, start: datetime, end: datetime, **filters) -> List[Dict[str, Any]]:
    """Fetch requests from LiteLLM PostgreSQL database

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime
        **filters: Optional filters (model, status, user, etc.)

    Returns:
        List of request dictionaries
    """
    query = """
        SELECT
            "startTime",
            "endTime",
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            "user",
            session_id,
            status,
            cache_hit,
            metadata->>'user_api_key_alias' as api_key_alias
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
    """

    params = [start, end]

    # Add optional filters
    if 'model' in filters:
        query += ' AND model LIKE %s'
        params.append(f"%{filters['model']}%")

    if 'status' in filters:
        query += ' AND status = %s'
        params.append(filters['status'])

    if 'user' in filters:
        query += ' AND "user" = %s'
        params.append(filters['user'])

    query += ' ORDER BY "startTime" DESC'

    if 'limit' in filters:
        query += f" LIMIT {filters['limit']}"

    return db.execute(query, tuple(params))


def get_sessions(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Fetch session data from LiteLLM

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of session dictionaries with aggregated metrics
    """
    query = """
        SELECT
            session_id,
            COUNT(*) as request_count,
            array_agg(DISTINCT model) as models,
            MIN("startTime") as session_start,
            MAX("endTime") as session_end,
            SUM(total_tokens) as total_tokens,
            SUM(prompt_tokens) as total_prompt_tokens,
            SUM(completion_tokens) as total_completion_tokens
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
            AND session_id IS NOT NULL
        GROUP BY session_id
        ORDER BY request_count DESC
    """

    return db.execute(query, (start, end))


def get_model_summary(db: Database, start: datetime, end: datetime, min_requests: int = 10) -> List[Dict[str, Any]]:
    """Get model usage summary with aggregated statistics

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime
        min_requests: Minimum requests to include in results

    Returns:
        List of model summaries
    """
    query = """
        SELECT
            model,
            COUNT(*) as total_requests,
            COUNT(*) FILTER (WHERE status = 'success') as success_count,
            COUNT(*) FILTER (WHERE status = 'failure') as failure_count,
            AVG(prompt_tokens) as avg_prompt_tokens,
            AVG(completion_tokens) as avg_completion_tokens,
            AVG(total_tokens) as avg_total_tokens,
            STDDEV(total_tokens) as stddev_total_tokens,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_tokens) as median_tokens,
            MIN(total_tokens) as min_tokens,
            MAX(total_tokens) as max_tokens,
            AVG(EXTRACT(EPOCH FROM ("endTime" - "startTime"))) as avg_duration_seconds,
            COUNT(*) FILTER (WHERE cache_hit = 'True') as cache_hits
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
        GROUP BY model
        HAVING COUNT(*) >= %s
        ORDER BY total_requests DESC
    """

    return db.execute(query, (start, end, min_requests))


def get_hourly_distribution(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get request distribution by hour

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of hourly request counts
    """
    query = """
        SELECT
            EXTRACT(HOUR FROM "startTime") as hour,
            COUNT(*) as requests
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
        GROUP BY hour
        ORDER BY hour
    """

    return db.execute(query, (start, end))


def get_daily_distribution(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get request distribution by day of week

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of daily request counts
    """
    query = """
        SELECT
            EXTRACT(DOW FROM "startTime") as day_of_week,
            COUNT(*) as requests
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
        GROUP BY day_of_week
        ORDER BY day_of_week
    """

    return db.execute(query, (start, end))


def get_api_key_usage(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get usage by API key

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of API key usage summaries
    """
    query = """
        SELECT
            COALESCE(metadata->>'user_api_key_alias', 'unknown') as api_key_alias,
            COUNT(*) as total_requests,
            COUNT(DISTINCT model) as unique_models,
            SUM(total_tokens) as total_tokens,
            MODE() WITHIN GROUP (ORDER BY model) as most_used_model
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
        GROUP BY api_key_alias
        ORDER BY total_requests DESC
    """

    return db.execute(query, (start, end))


def get_error_summary(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get error summary by model

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of error summaries
    """
    query = """
        SELECT
            model,
            COUNT(*) as error_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as error_percentage
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
            AND status = 'failure'
        GROUP BY model
        ORDER BY error_count DESC
    """

    return db.execute(query, (start, end))


def get_public_model_names(db: Database, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get public model names usage statistics

    Public model names are what clients call LiteLLM with (stored in model_group field).
    LiteLLM routes these to actual models (stored in model field).

    Args:
        db: Database connection
        start: Start datetime
        end: End datetime

    Returns:
        List of public model name statistics
    """
    query = """
        SELECT
            model_group as public_model,
            COUNT(*) as total_requests,
            COUNT(*) FILTER (WHERE status = 'success') as success_count,
            COUNT(*) FILTER (WHERE status = 'failure') as failure_count,
            ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / NULLIF(COUNT(*), 0), 1) as success_rate,
            SUM(total_tokens) as total_tokens,
            ROUND(AVG(total_tokens), 0) as avg_tokens,
            COUNT(DISTINCT model) as unique_actual_models,
            MODE() WITHIN GROUP (ORDER BY model) as most_used_actual_model
        FROM "LiteLLM_SpendLogs"
        WHERE "startTime" >= %s AND "startTime" < %s
            AND model_group IS NOT NULL
            AND model_group != ''
        GROUP BY model_group
        ORDER BY total_requests DESC
    """

    return db.execute(query, (start, end))