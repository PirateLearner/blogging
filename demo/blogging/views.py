from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from django.db import transaction

from blogging.models import Content, Policy
from django.utils import timezone
from django.db.models import Q

from blogging.settings import blog_settings

import json 
if blog_settings.USE_POLICY:
    from blogging.models import Policy
    
if blog_settings.USE_TEMPLATES:
    from blogging.models import Template
    from blogging.factory import CreateTemplate
    from importlib import import_module
    
# Create your views here.

def index(request):
    username = request.GET.get('author', None)
    pin = request.GET.get('pinned', None)
    if pin is not None:
        entries = Content.objects.get_pinned(publish_filter=True)
    else:
        entries = Content.objects.get_published()

    if username is not None:
        entries = entries.filter(author__username=username)
        
    context = {'entries': entries,}
    #from django.template import loader
    #template = loader.get_template("blogging/index.html")
    #return HttpResponse(template.render(context, request))
    template = "blogging/index.html"
    return render(request, template, context)

from django.contrib.auth.decorators import login_required

@login_required
def manage_content(request):
    username = request.GET.get('author', None)
    get_pinned = request.GET.get('pinned', None)
    draft_only = request.GET.get('drafts', None)
    publish_only = request.GET.get('published', None)
    if draft_only is not None and publish_only is not None:
        #Both are set, that implies get all
        draft_only = None
        publish_only = None
        
    filtermap = {'author': Q(author__username=username),
                 'draft' : Q(policy__policy=Policy.PUBLISH) & 
                           ( Q(policy__start__isnull=True) | 
                             Q(policy__start__gt= timezone.now()) |
                             (  Q(policy__start__lte=timezone.now()) & 
                                Q(policy__end__lt=timezone.now())
                              )
                            ),
                 'published':(Q(policy__policy=
                            Policy.PUBLISH)& Q(policy__start__lte=
                            timezone.now()) & (Q(policy__end__gt=
                            timezone.now()) | Q(policy__end__isnull=True))),
                 'pinned': (Q(policy__policy=
                            Policy.PIN)& Q(policy__start__lte=
                            timezone.now()) & (Q(policy__end__gt=
                            timezone.now()) | Q(policy__end__isnull=True)))}
    
    queryset = Content.objects.all().order_by('-create_date')
    
    if username is not None:
        queryset = queryset.filter(filtermap['author'])
    if get_pinned is not None:
        queryset = queryset.filter(filtermap['pinned'])
    if draft_only is not None:
        queryset = queryset.filter(filtermap['draft'])
    elif publish_only is not None:
        queryset = queryset.filter(filtermap['published'])
        
    context = {'entries': queryset,}
    #from django.template import loader
    #template = loader.get_template("blogging/index.html")
    #return HttpResponse(template.render(context, request))
    template = "blogging/list.html"
    return render(request, template, context)


def detail(request, blog_id):
    try:
        post = Content.objects.get(id=blog_id)
        if blog_settings.USE_TEMPLATES:
            template = None
            render_method = None
            if post.template is not None:
                template = post.template
            if template is not None:
                module = import_module('blogging.custom.'+\
                            CreateTemplate.get_file_name(template.name))
                render_method = getattr(module, 'render')
                post.text = render_method(post.text)
        context = {"entry": post}
        return render(request, "blogging/detail.html", context)
    except Content.DoesNotExist:
        raise Http404("Post does not exist")
        # NotFound response gives way for a custom page. We want to have one
        # 404 page for the entire project.
        #return HttpResponseNotFound("Post does not exist")
    return HttpResponse(post)

from django.views import View
from blogging.forms import ContentForm
from django.urls import reverse

from django.utils.decorators import method_decorator

class EditView(View):
    form_class = ContentForm
    template_name = "blogging/edit_rest.html" if blog_settings.USE_REST else "blogging/edit.html"
    
    @method_decorator(login_required, name='get')
    def get(self, request, blog_id):
        user = request.user
        form_class = self.form_class
        try:
            instance=Content.objects.get(id=blog_id) if blog_id is not None else None
        except Content.DoesNotExist:
            raise Http404("Trying to edit an entry that does not exist.")

        if blog_settings.USE_TEMPLATES:
            template_str = request.GET.get('template', None) if instance is None else None
            template = None
            if template_str is not None:
                template = Template.objects.get(name=template_str)
            elif instance is not None:
                template = instance.template
            
            if template is not None:
                form_name = CreateTemplate.get_form_name(template.name)
                module = import_module('blogging.custom.'+\
                            CreateTemplate.get_file_name(template.name))
                form_class = getattr(module, form_name)
        
        form = form_class(instance = instance)
        context={"entry": form}
        return render(request, self.template_name, context)
    
    @method_decorator(login_required, name='post')
    def post(self, request, blog_id):
        if 'Delete' in request.POST:
                return self.delete_entry(blog_id)
        if blog_id is None:
            instance = None
        else:
            try:
                instance = Content.objects.get(id=blog_id)
            except:
                raise Http404("Trying to save an entry that does not exist.")
        form_class = self.form_class
        if blog_settings.USE_TEMPLATES:
            template_id = request.POST.get('template', None)
            if template_id is not None and len(template_id) == 0:
                template_id = None
            if template_id is not None:
                template = Template.objects.get(id=template_id)
                form_name = CreateTemplate.get_form_name(template.name)
                module = import_module('blogging.custom.'+\
                            CreateTemplate.get_file_name(template.name))
                form_class = getattr(module, form_name)
        form = form_class(data=request.POST.copy(), instance=instance, 
                          initial={'author':request.user})
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            with transaction.atomic():
                instance.save()
                (policy, created) = Policy.objects.get_or_create(entry=instance, 
                                                                 policy=Policy.PUBLISH)
                if 'Publish' in request.POST:
                    if policy.end is not None:
                        if timezone.now() >= policy.end:
                            policy.end = None
                    if policy.start is None or policy.start > timezone.now():
                        policy.start = timezone.now()
                policy.save()
                
            if 'Publish' in request.POST:
                return HttpResponseRedirect(reverse('blogging:detail', 
                                                kwargs={"blog_id":instance.id}))
            else:
                return HttpResponseRedirect(reverse('blogging:edit', 
                                                kwargs={"blog_id":instance.id}))
        else:
            context  ={'entry': form}
            return render(request, self.template_name, context, status = 400)
    
    def delete_entry(self, blog_id):
        if blog_id is None:
            return HttpResponseRedirect(reverse('blogging:edit'))
        else:
            Content.objects.get(id=blog_id).delete()
            return HttpResponseRedirect(reverse('blogging:index'))

if blog_settings.USE_TEMPLATES:
    from blogging.forms import TemplateForm

    @login_required
    def manage_templates(request):
        username = request.GET.get('author', None)
        filtermap = {'author': Q(author__username=username),
                    }
        
        queryset = Template.objects.all().order_by('-create_date')
        
        if username is not None:
            queryset = queryset.filter(filtermap['author'])

        context = {'templates': queryset,}
        template = "blogging/template_list.html"
        return render(request, template, context)

    
    class TemplateView(View):
        form_class = TemplateForm
        template_name = "blogging/template.html"
        
        @method_decorator(login_required, name='get')
        def get(self, request, template_id):
            user = request.user
            form_class = self.form_class
            if template_id is None:
                form = form_class()
            else:
                try:
                    form = form_class(instance=Template.objects.get(id=
                                                                  template_id))
                except Content.DoesNotExist:
                    raise Http404("Trying to edit a template that does not exist.")
            context={"template": form}
            return render(request, self.template_name, context)
        
        @method_decorator(login_required, name='post')
        def post(self, request, template_id):
            if 'Delete' in request.POST:
                    return self.delete_entry(template_id)
            if template_id is None:
                instance = None
            else:
                try:
                    instance = Template.objects.get(id=template_id)
                except:
                    raise Http404("Trying to save a template that does not exist.")
            form_class = self.form_class
            form = form_class(request.POST, instance=instance)
            if form.is_valid():
                template = CreateTemplate(name=form.cleaned_data.get('name'),
                          members = json.loads(form.cleaned_data.get('fields')))
                if template.save():
                    instance = form.save(commit=False)
                    instance.author = request.user
                    instance.save()
                    return HttpResponseRedirect(reverse('blogging:template', 
                                            kwargs={"template_id":instance.id}))
                else:
                    context  ={'template': form}
                    return render(request, self.template_name, context, status = 400)
            else:
                #print('Form not valid')
                #print(form.errors)
                context  ={'template': form}
                return render(request, self.template_name, context, status = 400)
        
        def delete_entry(self, template_id):
            if template_id is None:
                return HttpResponseRedirect(reverse('blogging:template'))
            else:
                Template.objects.get(id=template_id).delete()
                return HttpResponseRedirect(reverse('blogging:template'))