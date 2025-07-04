"""
Tests for logs app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from logs.models import ExampleModel
from logs.services import create_example_record, get_example_data


class LogsModelTests(TestCase):
    """
    Tests for logs models.
    """
    
    def setUp(self):
        """Set up test data"""
        self.example = ExampleModel.objects.create(
            name="Test Example",
            description="Test Description"
        )
    
    def test_example_creation(self):
        """Test example model creation"""
        self.assertEqual(self.example.name, "Test Example")
        self.assertEqual(self.example.description, "Test Description")
        self.assertTrue(self.example.is_active)
    
    def test_example_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.example), "Test Example")


class LogsAPITests(APITestCase):
    """
    Tests for logs API endpoints.
    """
    
    def setUp(self):
        """Set up test data"""
        self.example = create_example_record("API Test Example", "API Test Description")
    
    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('logs-health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app'], 'logs')
    
    def test_example_get(self):
        """Test example GET endpoint"""
        url = reverse('logs-example')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_example_post_valid(self):
        """Test example POST endpoint with valid data"""
        url = reverse('logs-example')
        data = {
            'name': 'New Example',
            'description': 'New Description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_example_post_invalid(self):
        """Test example POST endpoint with invalid data"""
        url = reverse('logs-example')
        data = {}  # Empty data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogsServiceTests(TestCase):
    """
    Tests for logs services.
    """
    
    def test_create_example_record(self):
        """Test creating example record"""
        record = create_example_record("Service Test", "Service Description")
        self.assertEqual(record.name, "Service Test")
        self.assertEqual(record.description, "Service Description")
    
    def test_get_example_data(self):
        """Test getting example data"""
        create_example_record("Data Test", "Data Description")
        data = get_example_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
