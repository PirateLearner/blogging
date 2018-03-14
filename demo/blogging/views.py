from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

from blogging.models import Content
# Create your views here.

def index(request):
    posts = Content.objects.all()
    if len(posts) is 0:
        return HttpResponse("Hi, no posts have been created.")
    return HttpResponse(posts)

def detail(request, blog_id):
    try:
        post = Content.objects.get(id=blog_id)
        return HttpResponse(post)
    except Content.DoesNotExist:
        return HttpResponseNotFound("Post does not exist")
