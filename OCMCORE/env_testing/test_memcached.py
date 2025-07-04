#!/usr/bin/env python
"""
Test script to verify Memcached is working properly with Django.
Run this script to test the Memcached connection and basic operations.
"""

import os
import django
from django.core.cache import cache
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_memcached():
    """Test basic Memcached operations"""
    print("Testing Memcached connection...")
    
    try:
        # Test basic set/get operations
        cache.set('test_key', 'test_value', 60)
        result = cache.get('test_key')
        
        if result == 'test_value':
            print("✅ Memcached is working properly!")
            print(f"   Set/Get test passed: {result}")
        else:
            print("❌ Memcached set/get test failed")
            print(f"   Expected: 'test_value', Got: {result}")
            return False
        
        # Test cache deletion
        cache.delete('test_key')
        result_after_delete = cache.get('test_key')
        
        if result_after_delete is None:
            print("✅ Cache deletion test passed")
        else:
            print("❌ Cache deletion test failed")
            print(f"   Expected: None, Got: {result_after_delete}")
            return False
        
        # Test cache timeout
        cache.set('timeout_test', 'will_expire', 1)
        import time
        time.sleep(2)
        timeout_result = cache.get('timeout_test')
        
        if timeout_result is None:
            print("✅ Cache timeout test passed")
        else:
            print("❌ Cache timeout test failed")
            print(f"   Expected: None, Got: {timeout_result}")
            return False
        
        print("\n🎉 All Memcached tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Memcached test failed with error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Memcached is running: docker-compose up memcached")
        print("2. Check environment variables: MEMCACHED_HOST, MEMCACHED_PORT")
        print("3. Verify Memcached is accessible on the configured host/port")
        return False

if __name__ == '__main__':
    test_memcached() 