"""
Tests for cache app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from cache_utils import simple_cache


class CacheAppTests(APITestCase):
    """
    Tests for cache app API endpoints.
    """
    
    def setUp(self):
        """Set up test data"""
        # Add some test data to cache
        simple_cache.set('test_key', 'test_value', timeout=3600)
        simple_cache.set('test_key_2', 'test_value_2', timeout=3600)
    
    def test_cache_stats(self):
        """Test cache statistics endpoint"""
        url = reverse('cache-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_keys', response.data)
    
    def test_cache_keys(self):
        """Test cache keys endpoint"""
        url = reverse('cache-keys')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('keys', response.data)
        self.assertIn('total_keys', response.data)
    
    def test_cache_pattern_view(self):
        """Test cache pattern view endpoint"""
        url = reverse('cache-pattern-view')
        response = self.client.get(url, {'pattern': 'test_key'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('keys', response.data)
    
    def test_cache_pattern_stats(self):
        """Test cache pattern stats endpoint"""
        url = reverse('cache-pattern-stats')
        response = self.client.get(url, {'pattern': 'test_key'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pattern', response.data)
    
    def tearDown(self):
        """Clean up test data"""
        simple_cache.delete('test_key')
        simple_cache.delete('test_key_2') 