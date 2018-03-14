"""
@author: Anshul Thakur
"""
from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
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
    
    def save(self, *args, **kwargs):
        if len(self.title) == 0:
            if len(self.data)==0:
                raise ValidationError("Both title and data fields cannot be empty")
            else:
                title = self.data.split(' ')
                self.title = ' '.join(title[0: 9 if len(title)>10 else len(title)])
        
        super(Content, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title