from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from django.db import transaction

from blogging.models import Content, Policy
from django.utils import timezone
from django.db.models import Q

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
def manage(request):
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
    template_name = "blogging/edit.html"
    
    @method_decorator(login_required, name='get')
    def get(self, request, blog_id):
        user = request.user
        if blog_id is None:
            form = self.form_class(initial = {'author': user})
        else:
            try:
                form = self.form_class(instance=Content.objects.get(id=blog_id))
            except Content.DoesNotExist:
                raise Http404("Trying to edit an entry that does not exist.")
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
        form = self.form_class(request.POST, instance=instance)
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