#!/usr/bin/env python3
"""
Test script for pattern-based cache operations
Demonstrates how to use regex patterns to manage cache keys
"""

import time
import json
from core.simple_cache import simple_cache

def test_pattern_operations():
    """Test pattern-based cache operations"""
    print("🧪 Testing Pattern-Based Cache Operations")
    print("=" * 50)
    
    # Clear cache first
    simple_cache.clear()
    print("✅ Cache cleared")
    
    # Add some test data with different patterns
    test_data = {
        "user:profile:123": {"name": "John", "email": "john@example.com"},
        "user:profile:456": {"name": "Jane", "email": "jane@example.com"},
        "user:session:123": {"token": "abc123", "expires": "2024-01-01"},
        "user:session:456": {"token": "def456", "expires": "2024-01-01"},
        "config:app:production": {"debug": False, "version": "1.0"},
        "config:app:development": {"debug": True, "version": "1.0"},
        "rate_limit:api:user:123": 5,
        "rate_limit:api:user:456": 3,
        "attribution_abc123": {"data": "attribution_result_1"},
        "attribution_def456": {"data": "attribution_result_2"},
        "temp:cache:xyz": {"temp": "data"},
        "temp:cache:abc": {"temp": "data2"}
    }
    
    # Store test data
    for key, value in test_data.items():
        simple_cache.set(key, value, timeout=3600)
        print(f"✅ Stored: {key}")
    
    print(f"\n📊 Total keys in cache: {simple_cache.size()}")
    
    # Test 1: Get all user profile keys
    print("\n🔍 Test 1: Get all user profile keys")
    print("-" * 30)
    user_profile_keys = simple_cache.get_keys_by_pattern(r"user:profile:\d+")
    print(f"Pattern: user:profile:\\d+")
    print(f"Found keys: {user_profile_keys}")
    
    # Test 2: Get all user session keys
    print("\n🔍 Test 2: Get all user session keys")
    print("-" * 30)
    user_session_keys = simple_cache.get_keys_by_pattern(r"user:session:\d+")
    print(f"Pattern: user:session:\\d+")
    print(f"Found keys: {user_session_keys}")
    
    # Test 3: Get all user-related keys
    print("\n🔍 Test 3: Get all user-related keys")
    print("-" * 30)
    all_user_keys = simple_cache.get_keys_by_pattern(r"user:.*")
    print(f"Pattern: user:.*")
    print(f"Found keys: {all_user_keys}")
    
    # Test 4: Get all config keys
    print("\n🔍 Test 4: Get all config keys")
    print("-" * 30)
    config_keys = simple_cache.get_keys_by_pattern(r"config:.*")
    print(f"Pattern: config:.*")
    print(f"Found keys: {config_keys}")
    
    # Test 5: Get all rate limit keys
    print("\n🔍 Test 5: Get all rate limit keys")
    print("-" * 30)
    rate_limit_keys = simple_cache.get_keys_by_pattern(r"rate_limit:.*")
    print(f"Pattern: rate_limit:.*")
    print(f"Found keys: {rate_limit_keys}")
    
    # Test 6: Get all attribution keys
    print("\n🔍 Test 6: Get all attribution keys")
    print("-" * 30)
    attribution_keys = simple_cache.get_keys_by_pattern(r"attribution_.*")
    print(f"Pattern: attribution_.*")
    print(f"Found keys: {attribution_keys}")
    
    # Test 7: Get all temp keys
    print("\n🔍 Test 7: Get all temp keys")
    print("-" * 30)
    temp_keys = simple_cache.get_keys_by_pattern(r"temp:.*")
    print(f"Pattern: temp:.*")
    print(f"Found keys: {temp_keys}")
    
    # Test 8: Get values by pattern
    print("\n🔍 Test 8: Get values by pattern (user profiles)")
    print("-" * 30)
    user_profile_values = simple_cache.get_values_by_pattern(r"user:profile:\d+")
    print(f"Pattern: user:profile:\\d+")
    print(f"Found values: {json.dumps(user_profile_values, indent=2)}")
    
    # Test 9: Get pattern statistics
    print("\n🔍 Test 9: Get pattern statistics")
    print("-" * 30)
    user_stats = simple_cache.get_pattern_stats(r"user:.*")
    print(f"Pattern: user:.*")
    print(f"Statistics: {json.dumps(user_stats, indent=2)}")
    
    # Test 10: Delete keys by pattern
    print("\n🔍 Test 10: Delete temp keys by pattern")
    print("-" * 30)
    deleted_count = simple_cache.delete_keys_by_pattern(r"temp:.*")
    print(f"Pattern: temp:.*")
    print(f"Deleted {deleted_count} keys")
    
    # Verify deletion
    remaining_temp_keys = simple_cache.get_keys_by_pattern(r"temp:.*")
    print(f"Remaining temp keys: {remaining_temp_keys}")
    
    # Test 11: Refresh keys by pattern
    print("\n🔍 Test 11: Refresh user session keys")
    print("-" * 30)
    refreshed_count = simple_cache.refresh_keys_by_pattern(r"user:session:\d+", timeout=7200)
    print(f"Pattern: user:session:\\d+")
    print(f"Refreshed {refreshed_count} keys with 2-hour timeout")
    
    # Test 12: Complex pattern matching
    print("\n🔍 Test 12: Complex pattern matching")
    print("-" * 30)
    
    # Keys ending with specific numbers
    keys_ending_123 = simple_cache.get_keys_by_pattern(r".*123$")
    print(f"Pattern: .*123$ (keys ending with 123)")
    print(f"Found keys: {keys_ending_123}")
    
    # Keys containing specific words
    keys_with_api = simple_cache.get_keys_by_pattern(r".*api.*")
    print(f"Pattern: .*api.* (keys containing 'api')")
    print(f"Found keys: {keys_with_api}")
    
    # Test 13: Case insensitive pattern (if needed)
    print("\n🔍 Test 13: Case insensitive pattern")
    print("-" * 30)
    # Note: This would require case-insensitive regex flag
    # For now, we'll use a simple pattern
    config_keys_ci = simple_cache.get_keys_by_pattern(r"[Cc]onfig:.*")
    print(f"Pattern: [Cc]onfig:.* (config keys with case variation)")
    print(f"Found keys: {config_keys_ci}")
    
    # Test 14: Numeric range pattern
    print("\n🔍 Test 14: Numeric range pattern")
    print("-" * 30)
    # Keys with user IDs 100-500
    user_keys_range = simple_cache.get_keys_by_pattern(r"user:.*:(1[0-9][0-9]|2[0-9][0-9]|3[0-9][0-9]|4[0-9][0-9]|500)")
    print(f"Pattern: user:.*:(1[0-9][0-9]|2[0-9][0-9]|3[0-9][0-9]|4[0-9][0-9]|500)")
    print(f"Found keys: {user_keys_range}")
    
    # Final statistics
    print("\n📊 Final Cache Statistics")
    print("-" * 30)
    final_stats = simple_cache.get_stats()
    print(f"Total keys: {final_stats['size']}")
    print(f"All keys: {final_stats['keys']}")
    
    print("\n✅ Pattern-based cache operations test completed!")

def test_api_endpoints():
    """Test the API endpoints for pattern operations"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    # This would be tested with actual HTTP requests
    # For now, we'll show the expected API calls
    
    api_examples = [
        {
            "endpoint": "GET /api/cache/pattern/?pattern=user:profile:\\d+",
            "description": "Get all user profile keys"
        },
        {
            "endpoint": "GET /api/cache/pattern/?pattern=user:.*&values=true",
            "description": "Get all user-related keys with their values"
        },
        {
            "endpoint": "DELETE /api/cache/pattern/",
            "body": '{"pattern": "temp:.*"}',
            "description": "Delete all temp keys"
        },
        {
            "endpoint": "PUT /api/cache/pattern/",
            "body": '{"pattern": "user:session:\\d+", "timeout": 7200}',
            "description": "Refresh all user session keys with 2-hour timeout"
        },
        {
            "endpoint": "GET /api/cache/pattern/stats/?pattern=user:.*",
            "description": "Get statistics for all user-related keys"
        }
    ]
    
    for i, example in enumerate(api_examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   {example['endpoint']}")
        if 'body' in example:
            print(f"   Body: {example['body']}")

def test_regex_patterns():
    """Test various regex patterns"""
    print("\n🔍 Testing Regex Patterns")
    print("=" * 50)
    
    patterns = [
        {
            "pattern": r"user:profile:\d+",
            "description": "User profile keys with numeric IDs"
        },
        {
            "pattern": r"user:.*",
            "description": "All user-related keys"
        },
        {
            "pattern": r".*123$",
            "description": "Keys ending with 123"
        },
        {
            "pattern": r"config:app:.*",
            "description": "App configuration keys"
        },
        {
            "pattern": r"rate_limit:.*",
            "description": "All rate limit keys"
        },
        {
            "pattern": r"attribution_.*",
            "description": "All attribution keys"
        },
        {
            "pattern": r".*api.*",
            "description": "Keys containing 'api'"
        },
        {
            "pattern": r"user:.*:\d{3}",
            "description": "User keys with 3-digit IDs"
        }
    ]
    
    for pattern_info in patterns:
        pattern = pattern_info["pattern"]
        description = pattern_info["description"]
        
        keys = simple_cache.get_keys_by_pattern(pattern)
        print(f"\n📝 {description}")
        print(f"   Pattern: {pattern}")
        print(f"   Found: {len(keys)} keys")
        print(f"   Keys: {keys}")

if __name__ == "__main__":
    try:
        # Test pattern operations
        test_pattern_operations()
        
        # Test regex patterns
        test_regex_patterns()
        
        # Show API examples
        test_api_endpoints()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 