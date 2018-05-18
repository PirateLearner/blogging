'''
Created on 03-Apr-2018

@author: anshul
'''
from django.db import models
from django.db.models import Q
from blogging.settings import blog_settings
from django.utils import timezone

class ContentManager(models.Manager):
    def get_queryset(self):
        return super(ContentManager, self).get_queryset()
    
    def get_published(self):
        if not blog_settings.USE_POLICY:
            return self.get_queryset().filter(is_active=True)
        
        from blogging.models import Policy
        
        qs = self.get_queryset().filter(Q(policy__policy=
                                Policy.PUBLISH)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True)))
        return qs
    
    def get_pinned(self, publish_filter=False):
        if not blog_settings.USE_POLICY:
            from blogging.models import Content
            return Content.objects.none()
        
        from blogging.models import Policy
        
        qs = self.get_queryset().filter(Q(policy__policy=
                                Policy.PIN)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True)))
        if publish_filter:
            qs = qs.filter(Q(policy__policy=
                                Policy.PUBLISH)& Q(policy__start__lte=
                                timezone.now()) & (Q(policy__end__gt=
                                timezone.now()) | Q(policy__end__isnull=True)))
        return qs
    
