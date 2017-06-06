from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class BloggingApp(CMSApp):
    name = _('Blogging')
    urls = ['blogging.urls']
    app_name = 'blogging'

apphook_pool.register(BloggingApp)
