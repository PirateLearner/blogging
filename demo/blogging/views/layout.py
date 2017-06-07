import os

from blogging.utils import group_required, create_content_type, slugify_name
from blogging.forms import LayoutForm

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.urls import reverse

from django import forms
from django.forms.formsets import formset_factory
from django.views import View
from django.shortcuts import render

from django.core.paginator import Paginator , PageNotAnInteger, EmptyPage

from blogging.models import Layout
from blogging.utils import paginate

from blogging.forms import LayoutForm, FieldTypeForm

class LayoutListView(View):
    def get(self, request):
        if request.GET.get('new', None) is not None:
            #Return a form to create new layout
            form = LayoutForm()
            FieldFormSet = formset_factory(FieldTypeForm,extra=1)
            formset = FieldFormSet()
            page_context = {'form': form, 'formset':formset}
            return render(request,
                          'blogging/layout_form.html',
                          context=page_context)
        else:
            #Return a page of layouts
            layout_qs = Layout.objects.all()
            pages = paginate(request, layout_qs)
            
            page_context = {'layouts':pages}
            return render(request,
                          'blogging/layout_list.html',
                          context=page_context)

    def post(self, request):
        #Form submitted to create a new layout
        form1 = LayoutForm(request.POST)
        
        FieldFormSet = formset_factory(FieldTypeForm,extra=1)
        form2 = FieldFormSet(request.POST)
        
        if form1.is_valid() and form2.is_valid():
            try:
                form_dict = {}
                for form in form2:
                    form_dict[form.cleaned_data['field_name']] = form.cleaned_data['field_type']
                #Go ahead and create the file artifacts that are needed for this Layout
                is_leaf = False
                if form1.cleaned_data['layout_for'] == LayoutForm.CONTENT_TABLE:
                    is_leaf=True
                if (create_content_type(slugify_name(form1.cleaned_data['content_type']),
                                        form_dict,
                                        form1.cleaned_data['layout_for']) == False ):
                    raise forms.ValidationError("Some invalid parameter got passed.")
                
                layout_obj = form1.save() 
                #Save the schema in the layout model.
                layout_obj.schema = json.dumps(form_dict)
                layout_obj.save()

            except forms.ValidationError:
                layout_obj = None
                
            if layout_obj:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(new_obj._get_pk_val()), escape(new_obj)))
            else:
                page_context = {'form': form1,'formset':form2}
                return render(request,
                              'blogging/layout_form.html',
                              context=page_context)
            
        else:
            print "form is not valid form1 ", form1.is_valid(), " form 2 ", form2.is_valid()
            page_context = {'form': form1,'formset':form2}
            return render(request,
                          'blogging/layout_form.html',
                          context=page_context)

class LayoutView(View):
    def get(self, request, layout_id):
        if len(layout_id) > 0:
            try:
                layout = Layout.objects.get(int(layout_id))
                #The template demo page is in blogging/custom/<slug_name>/demo.html
                page_context = {'layout':layout}
                return render(request,
                              'blogging/layout_detail.html',
                              context=page_context)
            except Layout.DoesNotExist:
                raise Http404
        else:
            layout_qs = Layout.objects.all()
            pages = paginate(request, layout_qs)
            
            page_context = {'layouts':pages}
            return render(request,
                          'blogging/layout_list.html',
                          context=page_context)

    def post(self, request, layout_id):
        pass

#@group_required('Administrator','Author','Editor')
def layout_demo(request, layout_id):
    if len(layout_id) >0:
        try:
            layout = Layout.objects.get(int(layout_id))
            #The template demo page is in blogging/custom/<slug_name>/demo.html
            page_context = {'layout':layout}
            return render(request,
                          'blogging/custom/{slug}/demo.html'.format(slug=layout.model_name),
                          context=page_context)
        except Layout.DoesNotExist:
            raise Http404

@group_required('Administrator','Author','Editor')
def content_type(request):
    """
    This view asks the user to choose content type from the existing one or 
    create new content type to fit for his/her needs to create posts.
    
    Operations: 
    NEXT -- Go to next page for creation of New content based on selected 
            content type.
    DELETE -- Delete the current selected content type 
            (requires admin authorizations )
    NEW -- Create New content type.
    """
    if request.method == "POST":
        form = LayoutForm(request.POST)
        if form.is_valid():
            action = request.POST.get('submit')
            content_info = form.cleaned_data['Layout']

            if action == 'next':
                print content_info, type(content_info)
                request.session['content_info_id'] = content_info.id
                return HttpResponseRedirect(
                    reverse("blogging:create-post"))
            elif action == 'delete':
                if not request.user.is_staff:
                    # return permission denied
                    return HttpResponse(status=403)
                try:
                    filename = os.path.abspath(os.path.dirname(__file__))+"/custom/"+content_info.__str__().lower()+".py"
                    os.remove(filename)
                    filename = os.path.abspath(os.path.dirname(__file__))+"/templates/blogging/includes/"+content_info.__str__().lower()+".html"
                    os.remove(filename)
                    content_info.delete()
                except OSError as e: # this would be "except OSError, e:" before Python 2.6
                    raise # re-raise exception if a different error occured
            else:
                raise HttpResponseBadRequest
                
    else:
        if bool(request.user.groups.filter(name__in=['Author','Editor'])):
            request.session['content_info_id'] = 5
            return HttpResponseRedirect(
                    reverse("blogging:create-post"))

        if 'content_info_id' in request.session:
            try:
                content_info_obj = Layout.objects.get(
                    id=request.session['content_info_id']
                )
                data = { 'Layout':content_info_obj    }
                form = LayoutForm(initial=data)
            except ObjectDoesNotExist:
                del request.session['content_info_id']
                form = LayoutForm()
        else:
            form = LayoutForm()
    return render(request,
                  "blogging/content_type.html",
                  locals())


@group_required('Administrator')
def add_new_model(request, model_name):
    if (model_name.lower() == model_name):
        normal_model_name = model_name.capitalize()
    else:
        normal_model_name = model_name
    print normal_model_name
    
    if normal_model_name == 'Layout':
        if not request.user.is_staff:
            # return permission denied
            return HttpResponse(status=403)
        
        FieldFormSet = formset_factory(FieldTypeForm,extra=1)
        if request.method == 'POST':
            form1 = LayoutCreationForm(request.POST)
            form2 = FieldFormSet(request.POST)
            if form1.is_valid() and form2.is_valid():
                try:
                    form_dict = {}
                    for form in form2:
                        form_dict[form.cleaned_data['field_name']] = form.cleaned_data['field_type']
                    print "LOGS: Printing fomr dictionary: ", form_dict 
                        
                    
                    if (create_content_type(slugify_name(form1.cleaned_data['content_type']),form_dict,form1.cleaned_data['is_leaf']) == False ):
                        print 'Test'
                        raise forms.ValidationError("something got wronged")
                    new_obj = form1.save() #TODO many things
                    
                    print 'Test'
                    print new_obj.content_type
                except forms.ValidationError:
                    new_obj = None
                if new_obj:
                    return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(new_obj._get_pk_val()), escape(new_obj)))
                else:
                    page_context = {'form1': form1,'formset':form2,  'field': normal_model_name}
                    return render(request,
                                  'blogging/includes/add_content_type.html',
                                  context=page_context)
                
            else:
                print "form is not valid form1 ", form1.is_valid(), " form 2 ", form2.is_valid()     
                page_context = {'form1': form1,'formset':form2,  'field': normal_model_name}
                return render(request,
                              'blogging/includes/add_content_type.html',
                              context=page_context)
        else:
            form = LayoutCreationForm()
            formset = FieldFormSet()
            page_context = {'form1': form,'formset':formset,  'field': normal_model_name }
            return render(request,
                          'blogging/includes/add_content_type.html',
                          context=page_context)