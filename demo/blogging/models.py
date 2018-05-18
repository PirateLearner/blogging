"""
@author: Anshul Thakur
"""
from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from blogging.settings import blog_settings

from blogging import managers

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
    
    # Consult Policy table for this. This is just an inclusion flag that 'might' 
    # be useful while searching this table and filtering results.
    # Or, when we don't want the policy table at all (it's just a simple-minded 
    # blog)
    is_active = models.BooleanField(default=False)
    
    # @todo : The last modified filed should be updated only when the data field
    # or title field changes.
    last_modified = models.DateTimeField("Last modified", auto_now = True)
    
    objects = managers.ContentManager()
    
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

if blog_settings.USE_POLICY:
    from django.utils import timezone
    class Policy(models.Model):
        """
        Model for creating publishing policies on Blog Content
        Policies may include things like:
        - Publish Now
        - Unpublish Now
        - Pin Entry
        - Schedule Un-pin
        - Publication On Schedule
        - Unpublish on Schedule
        
        Publish is generalized to a schedule using start and stop dates.
        Similarly, Pinning is also generalized.
        
        The Publish Entry is created as soon as the key is assigned to the 
        post (first save) if Policy is enabled.
        """
        PUBLISH = 'PUB'
        PIN = 'PIN'
        
        POLICIES = ((PUBLISH, 'Publish'),
                    (PIN, 'Pin'),)
        
        entry = models.ForeignKey(Content, 
                                  on_delete = models.CASCADE, 
                                  related_name="policy")
        policy = models.CharField(max_length=5,
                                  choices = POLICIES,
                                  blank=True,
                                  default = None)
        start = models.DateTimeField("Policy Start Date", blank=True, null=True)
        end = models.DateTimeField("Policy End Date", blank=True, null=True)
        
        def is_published(self):
            if self.policy == self.PUBLISH:
                if self.start is not None and self.start <= timezone.now():
                    if self.end is None or self.end > timezone.now():
                        return True
                return False
            else:
                raise ValidationError("Invalid Policy type")
        
        def is_pinned(self):
            if self.policy == self.PIN:
                if self.start is not None and self.start <= timezone.now():
                    if self.end is None or self.end > timezone.now():
                        return True
                return False
            else:
                raise ValidationError("Invalid Policy type")
            
        def is_active(self):
            if self.start is not None and self.start <= timezone.now():
                if self.end is None or self.end > timezone.now():
                    return True
            return False

if blog_settings.USE_TEMPLATES is True:
    class Template(models.Model):
        name = models.CharField(max_length=15,
                                blank = False,
                                null = False)
        fields = models.TextField()
        author = models.ForeignKey(User,
                                   null = True,
                                   on_delete = models.SET_NULL,
                                   related_name="template")
            
        def save(self, *args, **kwargs):
            '''
            Ensure that the fields are saved as a valid JSON.
            '''
            import json
            try:
                layout = json.loads(self.fields)
                #Do something with this and generate the appropriate file
                super(Template, self).save(*args, **kwargs)
            except:
                raise ValidationError("Check JSON validity (are you passing a"+
                                      " dict, or a string?")
        
    class TemplateMap(models.Model):
        content = models.ForeignKey(Content, 
                                  related_name="mapped", 
                                  on_delete = models.CASCADE)
        template = models.ForeignKey(Template,
                                     default=1,
                                     on_delete=models.SET_DEFAULT)
        
        