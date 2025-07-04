"""
Business logic services for attribution generation
"""

from core.models import StoredProcedureCaller
from simple_cache import simple_cache
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import hashlib
import json
import numpy as np
import random
from django.conf import settings
from simple_cache import data_cache_service

def _generate_cache_key(beg_date, end_date, id1, id2, attributes):
    """Generate cache key from parameters"""
    params = {
        'beg_date': str(beg_date),
        'end_date': str(end_date),
        'id1': id1,
        'id2': id2,
        'attributes': sorted(attributes)  # Sort for consistent cache key
    }
    sorted_params = json.dumps(params, sort_keys=True)
    return hashlib.md5(sorted_params.encode()).hexdigest()

def generate_attribution_service(beg_date, end_date, id1, id2, attributes, db_alias='default'):
    """
    Generate attribution data with simple caching.
    """
    # Generate cache key
    cache_key = f"attribution_{_generate_cache_key(beg_date, end_date, id1, id2, attributes)}"
    
    # Try to get from cache first
    cached_data = simple_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # If not in cache, fetch from database
    proc_args = [
        beg_date,
        end_date,
        id1,
        id2,
        ','.join(attributes)
    ]
    sp = StoredProcedureCaller(db_alias=db_alias)
    results = sp.call('usp_generate_attribution', proc_args)
    
    # Cache the results for 1 hour
    simple_cache.set(cache_key, results, timeout=3600)
    
    return results

def generate_attribution_excel(beg_date, end_date, id1, id2, attributes, db_alias='default'):
    """
    Generate attribution data as Excel file.
    Uses the same cached data as the JSON service for consistency.
    """
    # Generate cache key
    cache_key = f"attribution_{_generate_cache_key(beg_date, end_date, id1, id2, attributes)}"
    
    # Try to get from cache first
    cached_data = simple_cache.get(cache_key)
    
    if cached_data:
        # Use cached data to create DataFrame
        df = pd.DataFrame(cached_data)
    else:
        # Fetch fresh data and cache it
        proc_args = [
            beg_date,
            end_date,
            id1,
            id2,
            ','.join(attributes)
        ]
        sp = StoredProcedureCaller(db_alias=db_alias)
        df = sp.as_dataframe('usp_generate_attribution', proc_args)
        
        # Cache the data for future use
        simple_cache.set(cache_key, df.to_dict('records'), timeout=3600)
    
    # Generate Excel file
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    filename = f"attribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return output, filename

# Read-only cache operations (Available in all environments)
def get_cache_stats():
    """Get cache statistics (Available in all environments)"""
    return simple_cache.get_stats()

def get_all_cache_keys():
    """Get list of all cache keys (Available in all environments)"""
    return {
        'keys': simple_cache.get_all_keys(),
        'total_keys': len(simple_cache.get_all_keys())
    }

# Pattern-based cache viewing operations (Available in all environments)
def get_keys_by_pattern(pattern):
    """Get keys matching a regex pattern (Available in all environments)"""
    keys = simple_cache.get_keys_by_pattern(pattern)
    return {
        'pattern': pattern,
        'keys': keys,
        'count': len(keys)
    }

def get_values_by_pattern(pattern):
    """Get key-value pairs for keys matching a regex pattern (Available in all environments)"""
    values = simple_cache.get_values_by_pattern(pattern)
    return {
        'pattern': pattern,
        'values': values,
        'count': len(values)
    }

def get_pattern_stats(pattern):
    """Get statistics for keys matching a pattern (Available in all environments)"""
    return simple_cache.get_pattern_stats(pattern)

# Cache management operations (Development only)
def clear_cache():
    """Clear all cache (Development only)"""
    simple_cache.clear()
    return {"message": "Cache cleared successfully"}

def delete_cache_key(key):
    """Delete a specific cache key (Development only)"""
    success = simple_cache.delete(key)
    return {"message": f"Key '{key}' {'deleted' if success else 'not found'}"}

def refresh_cache_key(key, timeout=3600):
    """Refresh timeout for a cache key (Development only)"""
    success = simple_cache.refresh(key, timeout)
    return {"message": f"Key '{key}' {'refreshed' if success else 'not found'}"}

def dump_cache_sync():
    """Synchronous dump cache to file (Development only)"""
    success = simple_cache.dump_cache_sync()
    return {"message": f"Cache {'dumped' if success else 'failed to dump'} to {simple_cache.dump_file}"}

def set_auto_dump_interval(interval_seconds):
    """Set auto-dump interval (Development only)"""
    simple_cache.set_auto_dump_interval(interval_seconds)
    return {
        "message": f"Auto-dump interval set to {interval_seconds} seconds",
        "interval_seconds": interval_seconds
    }

def stop_auto_dump():
    """Stop auto-dump (Development only)"""
    simple_cache.stop_auto_dump()
    return {"message": "Auto-dump stopped"}

def start_auto_dump(interval_seconds=300):
    """Start auto-dump with specified interval (Development only)"""
    simple_cache.set_auto_dump_interval(interval_seconds)
    return {
        "message": f"Auto-dump started with {interval_seconds}s interval",
        "interval_seconds": interval_seconds
    }

# Pattern-based cache management operations (Development only)
def delete_keys_by_pattern(pattern):
    """Delete all keys matching a regex pattern (Development only)"""
    deleted_count = simple_cache.delete_keys_by_pattern(pattern)
    return deleted_count

def refresh_keys_by_pattern(pattern, timeout=3600):
    """Refresh timeout for all keys matching a regex pattern (Development only)"""
    refreshed_count = simple_cache.refresh_keys_by_pattern(pattern, timeout)
    return refreshed_count

def generate_attribution_data(start_date, end_date, id1, id2, attributes):
    """
    Generate attribution data based on input parameters.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        id1 (str): First ID field name
        id2 (str): Second ID field name
        attributes (list): List of attribute names to include
    
    Returns:
        pandas.DataFrame: Generated attribution data
    """
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Calculate number of days
        days_diff = (end_dt - start_dt).days + 1
        
        # Generate sample data
        num_records = min(days_diff * 50, 1000)  # Max 1000 records for demo
        
        # Create date range
        dates = [start_dt + timedelta(days=i) for i in range(days_diff)]
        
        # Generate sample data
        data = []
        
        for _ in range(num_records):
            record = {
                'date': random.choice(dates).strftime('%Y-%m-%d'),
                id1: f"{id1}_{random.randint(1000, 9999)}",
                id2: f"{id2}_{random.randint(1000, 9999)}"
            }
            
            # Add attributes based on configuration
            for attr in attributes:
                if attr in ['revenue', 'conversions', 'clicks', 'impressions']:
                    # Numeric attributes
                    if attr == 'revenue':
                        record[attr] = round(random.uniform(10.0, 1000.0), 2)
                    elif attr == 'conversions':
                        record[attr] = random.randint(0, 50)
                    elif attr == 'clicks':
                        record[attr] = random.randint(10, 500)
                    elif attr == 'impressions':
                        record[attr] = random.randint(100, 10000)
                else:
                    # Text attributes
                    if attr == 'campaign_name':
                        campaigns = ['Summer Sale', 'Winter Campaign', 'Holiday Special', 'New Product Launch']
                        record[attr] = random.choice(campaigns)
                    elif attr == 'channel':
                        channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct']
                        record[attr] = random.choice(channels)
                    elif attr == 'device_type':
                        devices = ['Desktop', 'Mobile', 'Tablet']
                        record[attr] = random.choice(devices)
                    elif attr == 'geo_location':
                        locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
                        record[attr] = random.choice(locations)
                    elif attr == 'time_of_day':
                        times = ['Morning', 'Afternoon', 'Evening', 'Night']
                        record[attr] = random.choice(times)
                    elif attr == 'day_of_week':
                        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        record[attr] = random.choice(days)
                    else:
                        record[attr] = f"{attr}_value_{random.randint(1, 100)}"
            
            data.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Sort by date and IDs
        df = df.sort_values(['date', id1, id2]).reset_index(drop=True)
        
        return df
        
    except Exception as e:
        print(f"Error generating attribution data: {str(e)}")
        return pd.DataFrame()

# Your attribution service is already cached!
results = generate_attribution_service(beg_date, end_date, id1, id2, attributes)

# Cache user preferences
data_cache_service.set_user_data(user_id, user_preferences)

# Cache system configuration
data_cache_service.set_configuration('attribution_settings', config_data)

def analyze_securities_data(start_date, end_date, portfolio_data, benchmark_data, analysis_levels, analysis_types):
    """
    Analyze securities data and calculate attribution metrics.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        portfolio_data (dict): Portfolio securities data
        benchmark_data (dict): Benchmark securities data
        analysis_levels (list): Analysis levels ['daily', 'aggregate']
        analysis_types (list): Analysis types ['allocation', 'selection', 'interaction']
    
    Returns:
        dict: Analysis results with charts data
    """
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Calculate number of days
        days_diff = (end_dt - start_dt).days + 1
        
        # Generate daily data for the date range
        daily_data = generate_daily_securities_data(
            start_dt, end_dt, portfolio_data, benchmark_data
        )
        
        results = {
            'summary': {
                'date_range': f"{start_date} to {end_date}",
                'total_days': days_diff,
                'portfolio_securities': len(portfolio_data['securities']),
                'benchmark_securities': len(benchmark_data['securities'])
            },
            'daily_analysis': {},
            'aggregate_analysis': {},
            'charts': {}
        }
        
        # Perform daily level analysis
        if 'daily' in analysis_levels:
            results['daily_analysis'] = perform_daily_analysis(
                daily_data, analysis_types
            )
        
        # Perform aggregate level analysis
        if 'aggregate' in analysis_levels:
            results['aggregate_analysis'] = perform_aggregate_analysis(
                daily_data, analysis_types
            )
        
        # Generate charts data
        results['charts'] = generate_charts_data(
            daily_data, results['daily_analysis'], results['aggregate_analysis']
        )
        
        return results
        
    except Exception as e:
        print(f"Error analyzing securities data: {str(e)}")
        return {'error': str(e)}

def generate_daily_securities_data(start_dt, end_dt, portfolio_data, benchmark_data):
    """
    Generate daily securities data for the given date range.
    """
    daily_data = []
    
    for i in range((end_dt - start_dt).days + 1):
        current_date = start_dt + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Generate daily variations for portfolio
        portfolio_daily = {
            'date': date_str,
            'type': 'portfolio',
            'securities': portfolio_data['securities'],
            'weights': [w * (1 + random.uniform(-0.1, 0.1)) for w in portfolio_data['weights']],
            'contributions': [c * (1 + random.uniform(-0.2, 0.2)) for c in portfolio_data['contributions']],
            'revenues': [r * (1 + random.uniform(-0.15, 0.15)) for r in portfolio_data['revenues']]
        }
        
        # Normalize weights
        total_weight = sum(portfolio_daily['weights'])
        portfolio_daily['weights'] = [w / total_weight for w in portfolio_daily['weights']]
        
        # Generate daily variations for benchmark
        benchmark_daily = {
            'date': date_str,
            'type': 'benchmark',
            'securities': benchmark_data['securities'],
            'weights': [w * (1 + random.uniform(-0.1, 0.1)) for w in benchmark_data['weights']],
            'contributions': [c * (1 + random.uniform(-0.2, 0.2)) for c in benchmark_data['contributions']],
            'revenues': [r * (1 + random.uniform(-0.15, 0.15)) for r in benchmark_data['revenues']]
        }
        
        # Normalize weights
        total_weight = sum(benchmark_daily['weights'])
        benchmark_daily['weights'] = [w / total_weight for w in benchmark_daily['weights']]
        
        daily_data.append(portfolio_daily)
        daily_data.append(benchmark_daily)
    
    return daily_data

def perform_daily_analysis(daily_data, analysis_types):
    """
    Perform daily level attribution analysis.
    """
    daily_results = {}
    
    # Group data by date
    dates = sorted(list(set([d['date'] for d in daily_data])))
    
    for date in dates:
        date_data = [d for d in daily_data if d['date'] == date]
        portfolio = next(d for d in date_data if d['type'] == 'portfolio')
        benchmark = next(d for d in date_data if d['type'] == 'benchmark')
        
        daily_results[date] = calculate_attribution_effects(
            portfolio, benchmark, analysis_types
        )
    
    return daily_results

def perform_aggregate_analysis(daily_data, analysis_types):
    """
    Perform aggregate level attribution analysis.
    """
    # Calculate average portfolio and benchmark data
    portfolio_avg = calculate_average_data(daily_data, 'portfolio')
    benchmark_avg = calculate_average_data(daily_data, 'benchmark')
    
    return calculate_attribution_effects(
        portfolio_avg, benchmark_avg, analysis_types
    )

def calculate_average_data(daily_data, data_type):
    """
    Calculate average data for portfolio or benchmark.
    """
    type_data = [d for d in daily_data if d['type'] == data_type]
    
    if not type_data:
        return None
    
    # Get all unique securities
    all_securities = set()
    for data in type_data:
        all_securities.update(data['securities'])
    
    securities = list(all_securities)
    
    # Calculate averages
    avg_weights = []
    avg_contributions = []
    avg_revenues = []
    
    for security in securities:
        weights = []
        contributions = []
        revenues = []
        
        for data in type_data:
            if security in data['securities']:
                idx = data['securities'].index(security)
                weights.append(data['weights'][idx])
                contributions.append(data['contributions'][idx])
                revenues.append(data['revenues'][idx])
        
        avg_weights.append(sum(weights) / len(weights) if weights else 0)
        avg_contributions.append(sum(contributions) / len(contributions) if contributions else 0)
        avg_revenues.append(sum(revenues) / len(revenues) if revenues else 0)
    
    return {
        'type': data_type,
        'securities': securities,
        'weights': avg_weights,
        'contributions': avg_contributions,
        'revenues': avg_revenues
    }

def calculate_attribution_effects(portfolio, benchmark, analysis_types):
    """
    Calculate attribution effects (allocation, selection, interaction).
    """
    results = {}
    
    # Find common securities
    common_securities = list(set(portfolio['securities']) & set(benchmark['securities']))
    
    if 'allocation' in analysis_types:
        results['allocation'] = calculate_allocation_effect(portfolio, benchmark, common_securities)
    
    if 'selection' in analysis_types:
        results['selection'] = calculate_selection_effect(portfolio, benchmark, common_securities)
    
    if 'interaction' in analysis_types:
        results['interaction'] = calculate_interaction_effect(portfolio, benchmark, common_securities)
    
    return results

def calculate_allocation_effect(portfolio, benchmark, common_securities):
    """
    Calculate allocation effect: (Portfolio Weight - Benchmark Weight) * Benchmark Return
    """
    allocation_effects = {}
    
    for security in common_securities:
        p_idx = portfolio['securities'].index(security)
        b_idx = benchmark['securities'].index(security)
        
        portfolio_weight = portfolio['weights'][p_idx]
        benchmark_weight = benchmark['weights'][b_idx]
        benchmark_return = benchmark['contributions'][b_idx]
        
        allocation_effect = (portfolio_weight - benchmark_weight) * benchmark_return
        allocation_effects[security] = allocation_effect
    
    return allocation_effects

def calculate_selection_effect(portfolio, benchmark, common_securities):
    """
    Calculate selection effect: Benchmark Weight * (Portfolio Return - Benchmark Return)
    """
    selection_effects = {}
    
    for security in common_securities:
        p_idx = portfolio['securities'].index(security)
        b_idx = benchmark['securities'].index(security)
        
        benchmark_weight = benchmark['weights'][b_idx]
        portfolio_return = portfolio['contributions'][p_idx]
        benchmark_return = benchmark['contributions'][b_idx]
        
        selection_effect = benchmark_weight * (portfolio_return - benchmark_return)
        selection_effects[security] = selection_effect
    
    return selection_effects

def calculate_interaction_effect(portfolio, benchmark, common_securities):
    """
    Calculate interaction effect: (Portfolio Weight - Benchmark Weight) * (Portfolio Return - Benchmark Return)
    """
    interaction_effects = {}
    
    for security in common_securities:
        p_idx = portfolio['securities'].index(security)
        b_idx = benchmark['securities'].index(security)
        
        portfolio_weight = portfolio['weights'][p_idx]
        benchmark_weight = benchmark['weights'][b_idx]
        portfolio_return = portfolio['contributions'][p_idx]
        benchmark_return = benchmark['contributions'][b_idx]
        
        interaction_effect = (portfolio_weight - benchmark_weight) * (portfolio_return - benchmark_return)
        interaction_effects[security] = interaction_effect
    
    return interaction_effects

def generate_charts_data(daily_data, daily_analysis, aggregate_analysis):
    """
    Generate data for various chart types.
    """
    charts = {
        'daily_trends': generate_daily_trends_chart(daily_data),
        'allocation_comparison': generate_allocation_comparison_chart(daily_data),
        'contribution_analysis': generate_contribution_analysis_chart(daily_data),
        'attribution_breakdown': generate_attribution_breakdown_chart(daily_analysis, aggregate_analysis),
        'correlation_heatmap': generate_correlation_heatmap(daily_data),
        'performance_scatter': generate_performance_scatter_chart(daily_data)
    }
    
    return charts

def generate_daily_trends_chart(daily_data):
    """
    Generate line chart data for daily trends.
    """
    dates = sorted(list(set([d['date'] for d in daily_data])))
    
    # Calculate daily totals
    portfolio_totals = []
    benchmark_totals = []
    
    for date in dates:
        date_data = [d for d in daily_data if d['date'] == date]
        portfolio = next(d for d in date_data if d['type'] == 'portfolio')
        benchmark = next(d for d in date_data if d['type'] == 'benchmark')
        
        portfolio_totals.append(sum(portfolio['contributions']))
        benchmark_totals.append(sum(benchmark['contributions']))
    
    return {
        'type': 'line',
        'data': {
            'labels': dates,
            'datasets': [
                {
                    'label': 'Portfolio',
                    'data': portfolio_totals,
                    'borderColor': '#667eea',
                    'backgroundColor': 'rgba(102, 126, 234, 0.1)'
                },
                {
                    'label': 'Benchmark',
                    'data': benchmark_totals,
                    'borderColor': '#764ba2',
                    'backgroundColor': 'rgba(118, 75, 162, 0.1)'
                }
            ]
        }
    }

def generate_allocation_comparison_chart(daily_data):
    """
    Generate bar chart data for allocation comparison.
    """
    # Use the first day's data for comparison
    first_date = min([d['date'] for d in daily_data])
    date_data = [d for d in daily_data if d['date'] == first_date]
    portfolio = next(d for d in date_data if d['type'] == 'portfolio')
    benchmark = next(d for d in date_data if d['type'] == 'benchmark')
    
    return {
        'type': 'bar',
        'data': {
            'labels': portfolio['securities'],
            'datasets': [
                {
                    'label': 'Portfolio Weights',
                    'data': portfolio['weights'],
                    'backgroundColor': 'rgba(102, 126, 234, 0.8)'
                },
                {
                    'label': 'Benchmark Weights',
                    'data': [benchmark['weights'][benchmark['securities'].index(s)] if s in benchmark['securities'] else 0 for s in portfolio['securities']],
                    'backgroundColor': 'rgba(118, 75, 162, 0.8)'
                }
            ]
        }
    }

def generate_contribution_analysis_chart(daily_data):
    """
    Generate pie chart data for contribution analysis.
    """
    # Use the first day's data
    first_date = min([d['date'] for d in daily_data])
    date_data = [d for d in daily_data if d['date'] == first_date]
    portfolio = next(d for d in date_data if d['type'] == 'portfolio')
    
    return {
        'type': 'pie',
        'data': {
            'labels': portfolio['securities'],
            'datasets': [{
                'data': portfolio['contributions'],
                'backgroundColor': [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                    '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140'
                ]
            }]
        }
    }

def generate_attribution_breakdown_chart(daily_analysis, aggregate_analysis):
    """
    Generate stacked bar chart for attribution breakdown.
    """
    if not aggregate_analysis:
        return None
    
    securities = list(aggregate_analysis.get('allocation', {}).keys())
    
    allocation_data = [aggregate_analysis.get('allocation', {}).get(s, 0) for s in securities]
    selection_data = [aggregate_analysis.get('selection', {}).get(s, 0) for s in securities]
    interaction_data = [aggregate_analysis.get('interaction', {}).get(s, 0) for s in securities]
    
    return {
        'type': 'stacked_bar',
        'data': {
            'labels': securities,
            'datasets': [
                {
                    'label': 'Allocation Effect',
                    'data': allocation_data,
                    'backgroundColor': 'rgba(102, 126, 234, 0.8)'
                },
                {
                    'label': 'Selection Effect',
                    'data': selection_data,
                    'backgroundColor': 'rgba(118, 75, 162, 0.8)'
                },
                {
                    'label': 'Interaction Effect',
                    'data': interaction_data,
                    'backgroundColor': 'rgba(240, 147, 251, 0.8)'
                }
            ]
        }
    }

def generate_correlation_heatmap(daily_data):
    """
    Generate correlation heatmap data.
    """
    # Calculate correlations between portfolio and benchmark returns
    dates = sorted(list(set([d['date'] for d in daily_data])))
    
    portfolio_returns = []
    benchmark_returns = []
    
    for date in dates:
        date_data = [d for d in daily_data if d['date'] == date]
        portfolio = next(d for d in date_data if d['type'] == 'portfolio')
        benchmark = next(d for d in date_data if d['type'] == 'benchmark')
        
        portfolio_returns.append(sum(portfolio['contributions']))
        benchmark_returns.append(sum(benchmark['contributions']))
    
    # Calculate correlation
    correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
    
    return {
        'type': 'heatmap',
        'data': {
            'labels': ['Portfolio', 'Benchmark'],
            'datasets': [{
                'data': [
                    [1, correlation],
                    [correlation, 1]
                ],
                'backgroundColor': 'rgba(102, 126, 234, 0.8)'
            }]
        }
    }

def generate_performance_scatter_chart(daily_data):
    """
    Generate scatter plot for performance comparison.
    """
    dates = sorted(list(set([d['date'] for d in daily_data])))
    
    portfolio_returns = []
    benchmark_returns = []
    
    for date in dates:
        date_data = [d for d in daily_data if d['date'] == date]
        portfolio = next(d for d in date_data if d['type'] == 'portfolio')
        benchmark = next(d for d in date_data if d['type'] == 'benchmark')
        
        portfolio_returns.append(sum(portfolio['contributions']))
        benchmark_returns.append(sum(benchmark['contributions']))
    
    return {
        'type': 'scatter',
        'data': {
            'datasets': [{
                'label': 'Daily Performance',
                'data': list(zip(benchmark_returns, portfolio_returns)),
                'backgroundColor': 'rgba(102, 126, 234, 0.6)',
                'borderColor': '#667eea'
            }]
        }
    }

def create_securities_charts(df, analysis_levels, chart_types):
    """
    Create charts based on attribution DataFrame output.
    
    Args:
        df (pandas.DataFrame): Attribution data from generate_attribution_data
        analysis_levels (list): Analysis levels ['daily', 'aggregate']
        chart_types (list): Chart types to generate
    
    Returns:
        dict: Charts data for frontend
    """
    try:
        charts = {}
        
        # Ensure we have data to work with
        if df.empty:
            return {'error': 'No data available for chart generation'}
        
        # Generate charts based on requested types
        if 'line' in chart_types:
            charts['daily_trends'] = create_line_chart(df)
        
        if 'bar' in chart_types:
            charts['comparison_chart'] = create_bar_chart(df)
        
        if 'pie' in chart_types:
            charts['distribution_chart'] = create_pie_chart(df)
        
        if 'heatmap' in chart_types:
            charts['correlation_heatmap'] = create_heatmap_chart(df)
        
        if 'scatter' in chart_types:
            charts['scatter_plot'] = create_scatter_chart(df)
        
        # Add aggregate analysis if requested
        if 'aggregate' in analysis_levels:
            charts['aggregate_summary'] = create_aggregate_summary(df)
        
        return charts
        
    except Exception as e:
        print(f"Error creating charts: {str(e)}")
        return {'error': str(e)}

def create_line_chart(df):
    """
    Create line chart showing trends over time.
    """
    try:
        # Try to identify date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                break
        
        if date_col is None:
            # If no date column found, use index
            dates = list(range(len(df)))
        else:
            dates = df[date_col].astype(str).tolist()
        
        # Try to identify numeric columns for plotting
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns found for line chart'}
        
        # Use first few numeric columns
        datasets = []
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        
        for i, col in enumerate(numeric_cols[:3]):  # Limit to 3 columns
            datasets.append({
                'label': col,
                'data': df[col].tolist(),
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)].replace('#', 'rgba(') + ', 0.1)',
                'fill': False
            })
        
        return {
            'type': 'line',
            'data': {
                'labels': dates,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Attribution Data Trends'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }
        
    except Exception as e:
        return {'error': f'Error creating line chart: {str(e)}'}

def create_bar_chart(df):
    """
    Create bar chart for comparison.
    """
    try:
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns found for bar chart'}
        
        # Calculate averages for each numeric column
        averages = df[numeric_cols].mean()
        
        return {
            'type': 'bar',
            'data': {
                'labels': list(averages.index),
                'datasets': [{
                    'label': 'Average Values',
                    'data': averages.tolist(),
                    'backgroundColor': [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                        '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140'
                    ]
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Average Values by Column'
                    }
                }
            }
        }
        
    except Exception as e:
        return {'error': f'Error creating bar chart: {str(e)}'}

def create_pie_chart(df):
    """
    Create pie chart for distribution.
    """
    try:
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns found for pie chart'}
        
        # Calculate totals for each numeric column
        totals = df[numeric_cols].sum()
        
        return {
            'type': 'pie',
            'data': {
                'labels': list(totals.index),
                'datasets': [{
                    'data': totals.tolist(),
                    'backgroundColor': [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                        '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140'
                    ]
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Total Values Distribution'
                    }
                }
            }
        }
        
    except Exception as e:
        return {'error': f'Error creating pie chart: {str(e)}'}

def create_heatmap_chart(df):
    """
    Create correlation heatmap.
    """
    try:
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation heatmap'}
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Convert to format suitable for heatmap
        data = []
        for i, col1 in enumerate(numeric_cols):
            row = []
            for j, col2 in enumerate(numeric_cols):
                row.append(corr_matrix.iloc[i, j])
            data.append(row)
        
        return {
            'type': 'heatmap',
            'data': {
                'labels': numeric_cols,
                'datasets': [{
                    'data': data,
                    'backgroundColor': 'rgba(102, 126, 234, 0.8)'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Correlation Matrix'
                    }
                }
            }
        }
        
    except Exception as e:
        return {'error': f'Error creating heatmap: {str(e)}'}

def create_scatter_chart(df):
    """
    Create scatter plot.
    """
    try:
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for scatter plot'}
        
        # Use first two numeric columns
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Create data points
        data_points = []
        for i in range(len(df)):
            data_points.append({
                'x': df.iloc[i][x_col],
                'y': df.iloc[i][y_col]
            })
        
        return {
            'type': 'scatter',
            'data': {
                'datasets': [{
                    'label': f'{x_col} vs {y_col}',
                    'data': data_points,
                    'backgroundColor': 'rgba(102, 126, 234, 0.6)',
                    'borderColor': '#667eea'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{x_col} vs {y_col} Scatter Plot'
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': x_col
                        }
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': y_col
                        }
                    }
                }
            }
        }
        
    except Exception as e:
        return {'error': f'Error creating scatter plot: {str(e)}'}

def create_aggregate_summary(df):
    """
    Create aggregate summary statistics.
    """
    try:
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns found for summary'}
        
        # Calculate summary statistics
        summary = {
            'count': len(df),
            'columns': list(df.columns),
            'numeric_columns': numeric_cols,
            'statistics': {}
        }
        
        for col in numeric_cols:
            summary['statistics'][col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'sum': float(df[col].sum())
            }
        
        return summary
        
    except Exception as e:
        return {'error': f'Error creating summary: {str(e)}'} 