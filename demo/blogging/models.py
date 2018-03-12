"""
@author: Anshul Thakur
"""
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Content(models.Model):
    """
    Model for a raw blog database entry.
    """
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, 
                               on_delete = models.CASCADE, 
                               related_name="content")
    data = models.TextField()
    create_date = models.DateTimeField(auto_now_add = True)
    
    # @todo 
    last_modified = models.DateTimeField("Last modified", auto_now = True)