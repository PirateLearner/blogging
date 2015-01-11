from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from blogging import models
from blogging.forms import LatestEntriesForm, SectionPluginForm, ContactForm
from django.core.mail import send_mail, mail_admins

class BlogPlugin(CMSPluginBase):

    module = 'Blogging'


class LatestEntriesPlugin(BlogPlugin):

    render_template = models.LATEST_PLUGIN_TEMPLATES[0][0]
    name = _('Latest Blog Entries')
    model = models.LatestEntriesPlugin
    form = LatestEntriesForm

    def render(self, context, instance, placeholder):
        if instance and instance.template:
            self.render_template = instance.template
        context['instance'] = instance
#	context['nodes'] = self.model.get_post()
        return context

class SectionPlugin(BlogPlugin):
    render_template = 'blogging/plugin/plugin_section.html'
    name = _(' Blog Section Plugin ')
    model = models.SectionPlugin
    form = SectionPluginForm

class ContactPlugin(BlogPlugin):
    render_template = 'blogging/plugin/plugin_contact.html'
    name = _(' Contact Plugin ')
    model = models.ContactPlugin
    
    def create_form(self, instance, request):
        contact_type = request.GET.get('contact_type',None)
        
        
        if contact_type is None:
            contact_type = 'Queries'
        
        print "Contact form contact_type : ", contact_type
            
        if request.method == "POST":
            print "Contact form inside post"
            return ContactForm(data=request.POST)
        else:
            print "Contact form inside get"
            return ContactForm(initial={'contact_type':contact_type})    
    def render(self, context, instance, placeholder):
        request = context['request']

        form = self.create_form(instance, request)
#        instance.render_template = getattr(form, 'template', self.render_template)

        if request.method == "POST" and form.is_valid():
            subject = 'Contact mail from PirateLearner( ' + form.cleaned_data['contact_type'] + ' )'
            message = 'Name: ' + form.cleaned_data['name'] + '\n' + 'email: ' + form.cleaned_data['email'] + '\n Body: ' + form.cleaned_data['content']
            recipient_list = [instance.to_email]
            mail_admins(subject, message, fail_silently=False)
            context.update({
                'contact': instance,
            })
        else:
            context.update({
                'contact': instance,
                'form': form,
            })

        return context

plugin_pool.register_plugin(LatestEntriesPlugin)
plugin_pool.register_plugin(SectionPlugin)
plugin_pool.register_plugin(ContactPlugin)


