'''
Created on 02-Apr-2018

@author: anshul
'''
from django.conf import settings
from django.test.signals import setting_changed

DEFAULTS = {
    'USE_POLICY': True,
    }

class BlogSettings(object):
    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()
        
    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'BLOGGING', {})
        return self._user_settings
    
    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')
            
blog_settings = BlogSettings(None, DEFAULTS)

def reload_api_settings(*args, **kwargs):
    setting = kwargs['setting']
    if setting == 'BLOGGING':
        blog_settings.reload()


setting_changed.connect(reload_api_settings)