"""Output formatting - Console and JSON export"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from analytics.utils import format_duration, generate_timestamped_filename


class OutputFormatter:
    """Format and display analytics results"""

    def __init__(self):
        self.console = Console()

    def print_summary(self, summary: Dict[str, Any]):
        """Print executive summary panel"""
        self.console.print(Panel(
            f"[bold]Total Requests:[/bold] {summary['total_requests']}\n"
            f"[bold]Success Rate:[/bold] {summary['success_rate']:.1%}\n"
            f"[bold]Unique Models:[/bold] {summary['unique_models']}\n"
            f"[bold]Total Tokens:[/bold] {summary['total_tokens']:,}\n"
            f"[bold]Date Range:[/bold] {summary['days']} days",
            title="📊 Executive Summary",
            border_style="cyan"
        ))

    def print_model_stats(self, model_stats: Dict[str, Any], top_n: int = 20):
        """Print model usage statistics table with latency"""
        table = Table(title="🏆 Top Models by Usage")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Requests", justify="right", style="green")
        table.add_column("Success %", justify="right")
        table.add_column("Avg Latency", justify="right")
        table.add_column("P95 Latency", justify="right")
        table.add_column("Avg Tokens", justify="right")
        table.add_column("P95 Tokens", justify="right")

        # Sort by total requests
        sorted_models = sorted(
            model_stats.items(),
            key=lambda x: x[1]['total_requests'],
            reverse=True
        )[:top_n]

        for model, stats in sorted_models:
            tokens = stats.get('total_tokens', {})
            latency = stats.get('latency', {})

            avg_latency = latency.get('mean', 0)
            p95_latency = latency.get('p95', 0)

            avg_str = format_duration(avg_latency)
            p95_str = format_duration(p95_latency)

            table.add_row(
                model,
                str(stats['total_requests']),
                f"{stats['success_rate']:.1%}",
                avg_str,
                p95_str,
                f"{tokens.get('mean', 0):.0f}",
                f"{tokens.get('p95', 0):.0f}"
            )

        self.console.print(table)

    def print_temporal_patterns(self, temporal: Dict[str, Any]):
        """Print temporal patterns"""
        # Hourly distribution
        hourly_table = Table(title="📅 Hourly Distribution")
        hourly_table.add_column("Hour", style="cyan")
        hourly_table.add_column("Requests", justify="right", style="green")
        hourly_table.add_column("Bar", style="yellow")

        hourly = temporal.get('hourly', {})
        max_requests = max(hourly.values()) if hourly else 1

        for hour in range(24):
            count = hourly.get(hour, 0)
            bar_len = int(40 * count / max_requests) if max_requests > 0 else 0
            bar = "█" * bar_len

            hourly_table.add_row(
                f"{hour:02d}:00",
                str(count),
                bar
            )

        self.console.print(hourly_table)

        # Daily distribution
        daily_table = Table(title="📅 Day of Week Distribution")
        daily_table.add_column("Day", style="cyan")
        daily_table.add_column("Requests", justify="right", style="green")

        daily = temporal.get('daily', {})
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for day in day_order:
            daily_table.add_row(day, str(daily.get(day, 0)))

        self.console.print(daily_table)

        # Peak times
        if temporal.get('peak_hour') is not None:
            self.console.print(f"\n[bold]Peak Hour:[/bold] {temporal['peak_hour']:02d}:00")
        if temporal.get('peak_day'):
            self.console.print(f"[bold]Peak Day:[/bold] {temporal['peak_day']}")

    def print_session_analysis(self, sessions: List[Dict[str, Any]], top_n: int = 10):
        """Print session analysis"""
        table = Table(title="🔗 Top Sessions")
        table.add_column("Session ID", style="cyan", no_wrap=True)
        table.add_column("Requests", justify="right", style="green")
        table.add_column("Models", style="yellow")
        table.add_column("Total Tokens", justify="right")
        table.add_column("Duration", justify="right")

        for session in sessions[:top_n]:
            models = ', '.join(session['models'][:3])
            if len(session['models']) > 3:
                models += f" +{len(session['models']) - 3} more"

            # Calculate duration if we have start/end
            duration = "N/A"
            if session.get('session_start') and session.get('session_end'):
                try:
                    dur = session['session_end'] - session['session_start']
                    minutes = int(dur.total_seconds() / 60)
                    duration = f"{minutes}m"
                except:
                    pass

            table.add_row(
                session['session_id'][:20],
                str(session['request_count']),
                models,
                f"{session.get('total_tokens', 0):,}",
                duration
            )

        self.console.print(table)

    def print_api_key_usage(self, api_keys: List[Dict[str, Any]]):
        """Print API key usage breakdown"""
        table = Table(title="🔑 Request Sources (API Keys)")
        table.add_column("API Key", style="cyan")
        table.add_column("Requests", justify="right", style="green")
        table.add_column("Unique Models", justify="right")
        table.add_column("Most Used Model", style="yellow")

        for key in api_keys:
            table.add_row(
                key['api_key_alias'],
                str(key['total_requests']),
                str(key['unique_models']),
                key['most_used_model']
            )

        self.console.print(table)

    def print_error_analysis(self, errors: List[Dict[str, Any]]):
        """Print error analysis"""
        if not errors:
            self.console.print("\n✅ No errors found in the selected time period")
            return

        table = Table(title="❌ Errors by Model")
        table.add_column("Model", style="red")
        table.add_column("Error Count", justify="right")
        table.add_column("Error %", justify="right")

        for error in errors:
            table.add_row(
                error['model'],
                str(error['error_count']),
                f"{error['error_percentage']:.1f}%"
            )

        self.console.print(table)

    def print_public_model_names(self, public_models: List[Dict[str, Any]]):
        """Print public model names (what clients call LiteLLM with)"""
        if not public_models:
            self.console.print("\nℹ️  No public model name data found")
            return

        table = Table(title="🏷️  Public Model Names (Client Requests)")
        table.add_column("Public Model", style="cyan", no_wrap=True)
        table.add_column("Requests", justify="right", style="green")
        table.add_column("Success %", justify="right")
        table.add_column("Total Tokens", justify="right")
        table.add_column("Avg Tokens", justify="right")
        table.add_column("Routed To (This Period)", style="yellow")

        for pm in public_models:
            table.add_row(
                pm['public_model'],
                str(pm['total_requests']),
                f"{pm['success_rate']:.1f}%",
                f"{pm['total_tokens']:,}",
                f"{pm['avg_tokens']:.0f}",
                pm['most_used_actual_model'] if pm.get('most_used_actual_model') else "N/A"
            )

        self.console.print(table)

        # Add note about dynamic routing
        self.console.print("\n[i] Routing is dynamic - actual models used during this period shown above[/i]", style="dim")

    def print_performance_analysis(self, model_stats: Dict[str, Any], top_n: int = 20):
        """Print detailed performance profiling analysis"""
        self.console.print("\n" + "="*70, style="bold yellow")
        self.console.print("  ⚡ Performance Profiling (Analyzed Period)", style="bold yellow")
        self.console.print("="*70 + "\n", style="bold yellow")

        # Sort by total requests for relevance
        sorted_models = sorted(
            model_stats.items(),
            key=lambda x: x[1]['total_requests'],
            reverse=True
        )[:top_n]

        # Performance table
        table = Table(title="📊 Latency & Throughput Analysis")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Avg (s)", justify="right")
        table.add_column("Median (s)", justify="right")
        table.add_column("P95 (s)", justify="right")
        table.add_column("P99 (s)", justify="right")
        table.add_column("Std Dev", justify="right")
        table.add_column("Throughput (tok/s)", justify="right", style="green")

        for model, stats in sorted_models:
            latency = stats.get('latency', {})
            throughput = stats.get('throughput', {})

            if not latency:
                continue

            table.add_row(
                model,
                f"{latency.get('mean', 0):.2f}",
                f"{latency.get('median', 0):.2f}",
                f"{latency.get('p95', 0):.2f}",
                f"{latency.get('p99', latency.get('p95', 0)):.2f}",
                f"{latency.get('std', 0):.2f}",
                f"{throughput.get('median', 0):.0f}"
            )

        self.console.print(table)

        # Identify slow models
        slow_models = []
        for model, stats in model_stats.items():
            latency = stats.get('latency', {})
            if latency.get('p95', 0) > 30:  # P95 > 30 seconds
                slow_models.append({
                    'model': model,
                    'p95': latency.get('p95', 0),
                    'avg': latency.get('mean', 0),
                    'requests': stats['total_requests']
                })

        if slow_models:
            slow_models.sort(key=lambda x: x['p95'], reverse=True)

            self.console.print("\n⚠️  [bold red]Slow Models (P95 > 30s during analyzed period):[/bold red]")
            for sm in slow_models[:5]:
                self.console.print(f"   • {sm['model']}: P95={sm['p95']:.1f}s, Avg={sm['avg']:.1f}s ({sm['requests']} requests)")

        # Identify high-variance models
        high_variance = []
        for model, stats in model_stats.items():
            latency = stats.get('latency', {})
            if latency.get('std', 0) > latency.get('mean', 0):  # Std > mean indicates high variance
                high_variance.append({
                    'model': model,
                    'std': latency.get('std', 0),
                    'mean': latency.get('mean', 0),
                    'variance_ratio': latency.get('std', 0) / max(latency.get('mean', 1), 0.01)
                })

        if high_variance:
            high_variance.sort(key=lambda x: x['variance_ratio'], reverse=True)

            self.console.print("\n📈 [bold yellow]High Variance Models (unpredictable latency during analyzed period):[/bold yellow]")
            for hv in high_variance[:5]:
                self.console.print(f"   • {hv['model']}: Std={hv['std']:.1f}s (±{hv['variance_ratio']:.1f}x mean)")

        # Fastest models
        fast_models = []
        for model, stats in model_stats.items():
            if stats['total_requests'] >= 10:  # At least 10 requests for significance
                latency = stats.get('latency', {})
                throughput = stats.get('throughput', {})
                if latency and throughput:
                    fast_models.append({
                        'model': model,
                        'median_latency': latency.get('median', 0),
                        'throughput': throughput.get('median', 0)
                    })

        if fast_models:
            fast_models.sort(key=lambda x: x['throughput'], reverse=True)

            self.console.print("\n🚀 [bold green]Fastest Models during analyzed period (by throughput):[/bold green]")
            for fm in fast_models[:5]:
                self.console.print(f"   • {fm['model']}: {fm['throughput']:.0f} tok/s (median latency: {fm['median_latency']:.2f}s)")

        self.console.print()

    def export_json(self, results: Dict[str, Any], output_path: str = None):
        """Export results to JSON file

        Args:
            results: Analysis results dictionary
            output_path: Output file path (optional, auto-generated if not provided)
        """
        if not output_path:
            output_path = generate_timestamped_filename()

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Convert datetime and Decimal objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=json_serializer)

        self.console.print(f"\n📁 Exported to: [bold]{output_path}[/bold]")

    def print_full_report(self, results: Dict[str, Any]):
        """Print complete analytics report"""
        self.console.print("\n" + "="*70, style="bold cyan")
        self.console.print("  LiteLLM Usage Analytics Report", style="bold cyan")
        self.console.print(f"  Period: {results['start_date']} to {results['end_date']} ({results['days']} days)", style="cyan")
        self.console.print("="*70 + "\n", style="bold cyan")

        # Executive summary
        if 'summary' in results:
            self.print_summary(results['summary'])

        # Model usage
        if 'model_usage' in results:
            self.console.print()
            self.print_model_stats(results['model_usage'])

        # Temporal patterns
        if 'temporal' in results:
            self.console.print()
            self.print_temporal_patterns(results['temporal'])

        # Sessions
        if 'sessions' in results:
            self.console.print()
            self.print_session_analysis(results['sessions'])

        # API keys
        if 'api_keys' in results:
            self.console.print()
            self.print_api_key_usage(results['api_keys'])

        # Public model names
        if 'public_models' in results and results['public_models']:
            self.console.print()
            self.print_public_model_names(results['public_models'])

        # Performance profiling
        if 'model_usage' in results:
            self.print_performance_analysis(results['model_usage'])

        # Errors
        if 'errors' in results:
            self.console.print()
            self.print_error_analysis(results['errors'])

        self.console.print("\n" + "="*70 + "\n", style="bold cyan")