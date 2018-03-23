from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from blogging.models import Content


# Create your views here.

def index(request):
    entries = Content.objects.all()
    context = {'entries': entries,}
    #from django.template import loader
    #template = loader.get_template("blogging/index.html")
    #return HttpResponse(template.render(context, request))
    return render(request, "blogging/index.html", context)

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

class EditView(View):
    form_class = ContentForm
    template_name = "blogging/edit.html"
    
    def get(self, request, blog_id):
        blog_id=self.kwargs.get('blog_id', None)
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
    
    def post(self, request, blog_id):
        if blog_id is None:
            instance = None
        else:
            try:
                instance = Content.objects.get(id=blog_id)
            except:
                raise Http404("Trying to save an entry that does not exist.")
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            if 'Publish' in request.POST:
                return HttpResponseRedirect(reverse('blogging:detail', 
                                                kwargs={"blog_id":instance.id}))
            else:
                return HttpResponseRedirect(reverse('blogging:edit', 
                                                kwargs={"blog_id":instance.id}))
            