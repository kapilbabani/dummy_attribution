"""
Models for logs app.
"""

from django.db import models


class LogsModel(models.Model):
    """
    Base model for logs app.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Add your models here
class ExampleModel(LogsModel):
    """
    Example model for logs app.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'logs_example'
    
    def __str__(self):
        return self.name
