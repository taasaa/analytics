"""Statistical calculations - pure functions"""

from typing import List, Dict, Any
import statistics


def calculate_distribution(values: List[float]) -> Dict[str, float]:
    """Calculate distribution statistics for a list of values

    Args:
        values: List of numeric values

    Returns:
        Dictionary with mean, median, std, min, max, and percentiles
    """
    if not values:
        return {}

    sorted_vals = sorted(values)
    n = len(values)

    return {
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'std': statistics.stdev(values) if n > 1 else 0,
        'min': min(values),
        'max': max(values),
        'p25': sorted_vals[int(n * 0.25)],
        'p75': sorted_vals[int(n * 0.75)],
        'p90': sorted_vals[int(n * 0.90)],
        'p95': sorted_vals[int(n * 0.95)],
        'p99': sorted_vals[int(n * 0.99)],
    }


def analyze_model_usage(requests: List[Dict]) -> Dict[str, Any]:
    """Analyze usage statistics by model

    Args:
        requests: List of request dictionaries with 'model', tokens, and timestamps

    Returns:
        Dictionary keyed by model with statistics
    """
    by_model = {}

    for req in requests:
        model = req.get('model')
        if not model:
            continue

        if model not in by_model:
            by_model[model] = {
                'requests': [],
                'prompt_tokens': [],
                'completion_tokens': [],
                'total_tokens': [],
                'durations': [],
                'success_count': 0,
                'failure_count': 0,
            }

        by_model[model]['requests'].append(req)

        # Token statistics
        if 'prompt_tokens' in req:
            by_model[model]['prompt_tokens'].append(req['prompt_tokens'])
        if 'completion_tokens' in req:
            by_model[model]['completion_tokens'].append(req['completion_tokens'])
        if 'total_tokens' in req:
            by_model[model]['total_tokens'].append(req['total_tokens'])

        # Duration calculation
        if req.get('startTime') and req.get('endTime'):
            try:
                duration = (req['endTime'] - req['startTime']).total_seconds()
                by_model[model]['durations'].append(duration)
            except:
                pass

        # Success/failure tracking
        status = req.get('status', 'success')
        if status == 'success':
            by_model[model]['success_count'] += 1
        else:
            by_model[model]['failure_count'] += 1

    # Calculate statistics for each model
    results = {}
    for model, data in by_model.items():
        total_requests = len(data['requests'])

        # Calculate throughput (tokens/second) for successful requests
        throughput = []
        for i, req in enumerate(data['requests']):
            if req.get('status') == 'success' and i < len(data['durations']):
                duration = data['durations'][i]
                if duration > 0 and req.get('total_tokens', 0) > 0:
                    throughput.append(req['total_tokens'] / duration)

        results[model] = {
            'total_requests': total_requests,
            'success_count': data['success_count'],
            'failure_count': data['failure_count'],
            'success_rate': data['success_count'] / total_requests if total_requests > 0 else 0,
            'prompt_tokens': calculate_distribution(data['prompt_tokens']) if data['prompt_tokens'] else {},
            'completion_tokens': calculate_distribution(data['completion_tokens']) if data['completion_tokens'] else {},
            'total_tokens': calculate_distribution(data['total_tokens']) if data['total_tokens'] else {},
            'latency': calculate_distribution(data['durations']) if data['durations'] else {},
            'throughput': calculate_distribution(throughput) if throughput else {},
        }

    return results


def analyze_temporal_patterns(requests: List[Dict]) -> Dict[str, Any]:
    """Analyze temporal patterns (hourly, daily, weekly)

    Args:
        requests: List of request dictionaries with 'startTime'

    Returns:
        Dictionary with hourly, daily, weekly distributions
    """
    hourly = {i: 0 for i in range(24)}
    daily = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0}
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    for req in requests:
        start_time = req.get('startTime')
        if not start_time:
            continue

        try:
            hourly[start_time.hour] += 1
            daily[day_names[start_time.weekday()]] += 1
        except:
            pass

    # Find peak times
    peak_hour = max(hourly, key=hourly.get) if any(hourly.values()) else None
    peak_day = max(daily, key=daily.get) if any(daily.values()) else None

    return {
        'hourly': hourly,
        'daily': daily,
        'peak_hour': peak_hour,
        'peak_day': peak_day,
    }