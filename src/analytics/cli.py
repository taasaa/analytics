"""Command-line interface for analytics platform"""

import click
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os

from analytics.db import Database
from analytics.sources import get_source
from analytics.statistics import analyze_model_usage, analyze_temporal_patterns
from analytics.output import OutputFormatter
from analytics.utils import generate_timestamped_filename, parse_date


# Load environment variables
load_dotenv()


@click.command()
@click.option('--source', '-s', default='litellm', help='Data source name (default: litellm)')
@click.option('--days', '-d', default=14, help='Number of days to analyze (default: 14)')
@click.option('--start', 'start_date', help='Start date (YYYY-MM-DD)')
@click.option('--end', 'end_date', help='End date (YYYY-MM-DD)')
@click.option('--model', '-m', help='Filter to specific model (supports partial match)')
@click.option('--format', 'output_format', type=click.Choice(['console', 'json', 'all']),
              default='all', help='Output format (default: all)')
@click.option('--output', '-o', 'output_path', help='Output directory for exports')
@click.option('--min-requests', default=10, help='Minimum requests for model inclusion (default: 10)')
@click.option('--top-n', default=20, help='Number of top items to show (default: 20)')
@click.option('--test-db', is_flag=True, help='Test database connection and exit')
def main(source, days, start_date, end_date, model, output_format, output_path,
         min_requests, top_n, test_db):
    """Analyze usage patterns from data sources

    Examples:
        analytics --source litellm --days 14
        analytics --source litellm --start 2026-03-01 --end 2026-03-14
        analytics --source litellm --model gpt-4 --days 7
        analytics --source litellm --format json --output ./reports/
    """

    # Initialize database connection
    db = Database()

    # Test database connection if requested
    if test_db:
        if db.test_connection():
            click.echo("✅ Database connection successful")
        else:
            click.echo("❌ Database connection failed", err=True)
            raise SystemExit(1)
        return

    # Determine date range
    end_dt = parse_date(end_date) or datetime.now()
    start_dt = parse_date(start_date) or (end_dt - timedelta(days=days))

    # Initialize output formatter
    formatter = OutputFormatter()

    try:
        # Get source functions
        get_requests, get_sessions = get_source(source)

        click.echo(f"Fetching data from {source} for {days} days...")

        filters = {}
        if model:
            filters['model'] = model

        requests = get_requests(db, start_dt, end_dt, **filters)

        if not requests:
            click.echo(f"No data found for the specified period", err=True)
            raise SystemExit(0)

        click.echo(f"Found {len(requests)} requests")
        click.echo("Analyzing data...")

        total_requests = len(requests)

        results = {
            'source': source,
            'start_date': start_dt.isoformat(),
            'end_date': end_dt.isoformat(),
            'days': days,
            'total_requests': total_requests,
        }

        # Summary stats
        results['summary'] = {
            'total_requests': total_requests,
            'success_rate': sum(1 for r in requests if r.get('status') == 'success') / total_requests,
            'unique_models': len(set(r.get('model') for r in requests if r.get('model'))),
            'total_tokens': sum(r.get('total_tokens', 0) for r in requests),
            'days': days,
        }

        results['model_usage'] = analyze_model_usage(requests)

        results['temporal'] = analyze_temporal_patterns(requests)

        click.echo("Fetching session data...")
        sessions = get_sessions(db, start_dt, end_dt)
        results['sessions'] = sessions[:top_n]

        # API key usage (if available)
        try:
            from analytics.sources.litellm import get_api_key_usage
            click.echo("Analyzing API key usage...")
            api_keys = get_api_key_usage(db, start_dt, end_dt)
            results['api_keys'] = api_keys[:top_n]
        except ImportError:
            pass

        # Errors (if any)
        try:
            from analytics.sources.litellm import get_error_summary
            errors = get_error_summary(db, start_dt, end_dt)
            results['errors'] = errors
        except ImportError:
            pass

        # Public model names (what clients call LiteLLM with)
        try:
            from analytics.sources.litellm import get_public_model_names
            click.echo("Analyzing public model names...")
            public_models = get_public_model_names(db, start_dt, end_dt)
            results['public_models'] = public_models
        except ImportError:
            pass

        # Output results
        if output_format in ['console', 'all']:
            formatter.print_full_report(results)

        if output_format in ['json', 'all']:
            if output_path:
                output_file = Path(output_path) / generate_timestamped_filename()
            else:
                output_file = generate_timestamped_filename()

            formatter.export_json(results, str(output_file))

        click.echo(f"\n✅ Analysis complete!")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()