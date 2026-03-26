"""Unit tests for statistical calculations"""

import pytest
from analytics.statistics import calculate_distribution, analyze_model_usage
from datetime import datetime, timedelta


def test_calculate_distribution_basic():
    """Test basic distribution calculations"""
    values = [1, 2, 3, 4, 5]

    result = calculate_distribution(values)

    assert result['mean'] == 3.0
    assert result['median'] == 3
    assert result['min'] == 1
    assert result['max'] == 5
    assert result['p25'] == 2
    assert result['p75'] == 4
    assert result['p90'] == 5
    assert result['p95'] == 5


def test_calculate_distribution_empty():
    """Test empty input"""
    result = calculate_distribution([])

    assert result == {}


def test_calculate_distribution_single_value():
    """Test single value input"""
    result = calculate_distribution([42])

    assert result['mean'] == 42
    assert result['median'] == 42
    assert result['std'] == 0  # Can't calculate stdev for single value


def test_calculate_distribution_percentiles():
    """Test percentile calculations with larger dataset"""
    values = list(range(1, 101))  # 1 to 100

    result = calculate_distribution(values)

    # Percentiles are approximate using index positions
    assert result['p25'] == pytest.approx(25, abs=1)
    assert result['p75'] == pytest.approx(75, abs=1)
    assert result['p90'] == pytest.approx(90, abs=1)
    assert result['p95'] == pytest.approx(95, abs=1)


def test_analyze_model_usage_basic():
    """Test model usage analysis"""
    base_time = datetime(2026, 3, 26, 12, 0, 0)

    requests = [
        {
            'model': 'gpt-4',
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150,
            'startTime': base_time,
            'endTime': base_time + timedelta(seconds=2),
            'status': 'success'
        },
        {
            'model': 'gpt-4',
            'prompt_tokens': 200,
            'completion_tokens': 100,
            'total_tokens': 300,
            'startTime': base_time + timedelta(hours=1),
            'endTime': base_time + timedelta(hours=1, seconds=3),
            'status': 'success'
        },
        {
            'model': 'claude-3',
            'prompt_tokens': 150,
            'completion_tokens': 75,
            'total_tokens': 225,
            'startTime': base_time + timedelta(hours=2),
            'endTime': base_time + timedelta(hours=2, seconds=2.5),
            'status': 'success'
        }
    ]

    result = analyze_model_usage(requests)

    # Check we have both models
    assert 'gpt-4' in result
    assert 'claude-3' in result

    # Check gpt-4 stats
    gpt4 = result['gpt-4']
    assert gpt4['total_requests'] == 2
    assert gpt4['success_count'] == 2
    assert gpt4['failure_count'] == 0
    assert gpt4['success_rate'] == 1.0

    # Check token statistics
    assert gpt4['prompt_tokens']['mean'] == 150.0
    assert gpt4['total_tokens']['median'] == 225

    # Check latency
    assert 'mean' in gpt4['latency']
    assert gpt4['latency']['mean'] == pytest.approx(2.5, rel=0.01)


def test_analyze_model_usage_with_failures():
    """Test model usage with failed requests"""
    base_time = datetime(2026, 3, 26, 12, 0, 0)

    requests = [
        {
            'model': 'gpt-4',
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150,
            'startTime': base_time,
            'endTime': base_time + timedelta(seconds=2),
            'status': 'success'
        },
        {
            'model': 'gpt-4',
            'prompt_tokens': 200,
            'completion_tokens': 0,
            'total_tokens': 200,
            'startTime': base_time + timedelta(hours=1),
            'endTime': base_time + timedelta(hours=1, seconds=3),
            'status': 'failure'
        }
    ]

    result = analyze_model_usage(requests)

    gpt4 = result['gpt-4']
    assert gpt4['total_requests'] == 2
    assert gpt4['success_count'] == 1
    assert gpt4['failure_count'] == 1
    assert gpt4['success_rate'] == 0.5