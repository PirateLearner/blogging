from django.contrib import admin

# Register your models here.
from .models import Content, Policy

admin.site.register(Content)
admin.site.register(Policy)