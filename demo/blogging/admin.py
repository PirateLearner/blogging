from django.contrib import admin

# Register your models here.
from .models import Content, Policy, Template

admin.site.register(Content)
admin.site.register(Policy)
admin.site.register(Template)