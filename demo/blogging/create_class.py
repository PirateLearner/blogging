
class CreateClass():
    """ 
    This class will generate the required class of desired content type
    and form the string that will be written to the python script file
    """
    def __init__(self, name, member_dict,is_leaf):
        
        self.name = name
        self.member_dict = member_dict
        self.is_leaf = is_leaf
        
        #Headers
        self.import_string = None
        self.file_start = None
        
        #Form Generation
        self.form_name = None 
        # List to store the member of the Class
        self.form_member_string_list = [ ]
        self.form_initfunction_string = None
        self.class_formclass_save_string = None
        
        #Model Generation
        self.model_member_string_list = []
        self.model_name = None
        self.model_initfunction_pre_super_string = None
        self.model_initfunction_post_super_string = None
        self.model_init_function_body = None
        self.model_save_function_body = None
        
        self.setup_headers()
        
        self.create_model()
        #Generate Form
        self.create_form()
        
        
    def setup_headers(self):
        self.import_string = \
            'from blogging import tag_lib\n' +\
            'from blogging.models import *\n' +\
            'from django import forms\n' +\
            'from blogging.forms import *\n' +\
            'from ckeditor_uploader.widgets import CKEditorUploadingWidget\n' +\
            'import json\n' + \
            'from django.db import models \n' +\
            'from django.db.models import Q \n' +\
            'from mptt.forms import TreeNodeChoiceField\n' +\
            'from taggit.models import Tag \n' +\
            'import blogging \n'
        
        self.file_start =  \
        '"""\n' +\
        'This is auto generated script file.\n' +\
        'It defines the wrapper class for specified content type.\n'+\
        '"""\n'

    def create_form(self):
        
        if self.is_leaf is True:
            self.form_name = 'class ' + str(self.name).capitalize() +'Form(ContentForm):\n'
        else:
            self.form_name = 'class ' + str(self.name).capitalize() +'Form(SectionForm):\n'
        # add the title, section and tag fields
        
        self.form_member_string_list.append('\ttitle = forms.CharField(max_length = 100)\n')
        self.form_member_string_list.append('\tpid_count = forms.IntegerField(required=False)\n')
        if self.is_leaf == True:
            self.form_member_string_list.append('\tsection = TreeNodeChoiceField(queryset=Section.objects.all().filter(~Q(title="Orphan"),Q(children=None)),required=True,empty_label=None, label = "Select Section" )\n')
            
        else:
            self.form_member_string_list.append('\tparent = TreeNodeChoiceField(queryset=Section.objects.all().filter(~Q(title="Orphan"),~Q(title="Blog")),required=True,empty_label=None, label = "Select Parent" )\n')
        
        # string for init function
        self.form_initfunction_string = '\tdef __init__(self,action, *args, **kwargs):\n'
        self.form_initfunction_string += '\t\tinstance = kwargs.pop("instance", None)\n\t\tif instance:\n'
        self.form_initfunction_string += '\t\t\tjson_data = json.loads(instance.data)\n'
        self.form_initfunction_string += '\t\t\tkwargs.update(initial={\n'
        self.form_initfunction_string += '\t\t\t\t"title": instance.title,\n'
        self.form_initfunction_string += '\t\t\t\t"pid_count": json_data["pid_count"],\n'
        if is_leaf == True:
            self.form_initfunction_string += '\t\t\t\t"section": instance.section,\n'
            self.form_initfunction_string += '\t\t\t\t"tags": instance.tags.all(),\n'
        else:
            self.form_initfunction_string += '\t\t\t\t"parent": instance.parent,\n'


        #string for save function
        self.class_formclass_save_string = '\tdef save(self,post,commit=False):\n' + '\t\tpost.pop("csrfmiddlewaretoken")\n\t\tpost.pop("submit")\n' 
        self.class_formclass_save_string += '\t\tpost.pop("title")\n' 
        if is_leaf == True:
            self.class_formclass_save_string += '\t\tpost.pop("section")\n'
            self.class_formclass_save_string += '\t\tpost.pop("tags")\n'
        else:
            self.class_formclass_save_string += '\t\tpost.pop("parent")\n'
        
        # commit False case
        self.class_formclass_save_string += '\t\tif commit == False:\n'
        self.class_formclass_save_string += '\t\t\tfor k,v in post.iteritems():\n\t\t\t\tif str(k) == "pid_count" :\n\t\t\t\t\tpost["pid_count"] = self.cleaned_data["pid_count"]\n'
        self.class_formclass_save_string += '\t\t\t\telse:\n\t\t\t\t\tpost[k] = str(v.encode("utf-8"))\n'
        self.class_formclass_save_string += '\t\t\treturn json.dumps(post.dict())\n'
        
        # commit True Test
        self.class_formclass_save_string += '\t\tfor k,v in post.iteritems():\n\t\t\tif str(k) != "pid_count" :\n\t\t\t\ttmp = {}\n'
        self.class_formclass_save_string += '\t\t\t\ttmp = tag_lib.insert_tag_id(str(v.encode("utf-8")), self.cleaned_data["pid_count"])\n'
        self.class_formclass_save_string += '\t\t\t\tpost[k] = tmp["content"]\n'
        self.class_formclass_save_string += '\t\t\t\tpost["pid_count"] = tmp["pid_count"]\n'
        self.class_formclass_save_string += '\t\treturn json.dumps(post.dict())\n'
        
        
        for member_name, member_type in self.member_dict.iteritems():
            ## Creating form fields in FormClass
            if str(member_type) == 'TextField':
                class_member = '\t' + member_name + ' = forms.CharField(widget = CKEditorWidget(config_name="author"), required=False)\n'
            elif str(member_type) == 'CharField':
                class_member = '\t' + member_name + ' = forms.CharField(max_length=100, required=False)\n'
            self.form_member_string_list.append(class_member)

            self.form_initfunction_string += '\t\t\t\t"' + member_name + '":json_data["'+ member_name + '"],\n'

        self.form_initfunction_string += '\t\t\t\t})\n'
        if self.is_leaf == True:
            self.form_member_string_list.append('\ttags = Select2ChoiceField(queryset=Tag.objects.filter())\n')

        self.form_initfunction_string += '\t\tsuper(' + str(self.name).capitalize() +'Form' + ', self).__init__(*args, **kwargs)\n\n\n\n'

    
    def create_model(self):
        def create_init():
            self.model_init_function_body = \
                "\tdef __init__(self, *args, **kwargs):\n"
            self.model_init_function_body += self.model_initfunction_pre_super_string
            self.model_init_function_body += \
                "\t\tsuper("+str(self.name).capitalize()+", self).__init__(*args, **kwargs)\n"+\
                "\t\tdelattr(self, 'data')\n"
            self.model_init_function_body += self.model_initfunction_post_super_string

        def create_save():
            self.model_save_function_body = \
                "\tdef save(self, *args, **kwargs):\n"+\
                "\t\tif self.id is not None:"
            if self.is_leaf is True:
                self.model_save_function_body += \
                "\t\t\t"+self.name.lower()+" = blogging.models.Content.objects.get(id=self.id)\n"+\
                "\t\telse:\n"+\
                "\t\t\t"+self.name.lower()+" = blogging.models.Content()\n"
                self.model_save_function_body += \
                "\t\t"+self.name.lower()+".title = self.title\n"+\
                "\t\t"+self.name.lower()+".section = self.section\n"+\
                "\t\t"+self.name.lower()+".tags = self.tags\n"+\
                "\t\t"+self.name.lower()+".author = self.author\n"+\
                "\t\t"+self.name.lower()+".slug = self.slug\n\n"+\
                "\t\t"+self.name.lower()+".content_type = "+\
                    "Content.objects.filter(content_type=__name__.split('.')[-1])[0]\n\n"+\
                "\t\tpost_content = {}\n"+\
                "\t\tpost_content['pid_cont'] = self.pid_count\n\n"+\
                "\t\tfields = kwargs.pop('fields')\n"+\
                "\t\tfor field in fields:\n"+\
                "\t\t\tpost_content[field] = getattr(self,field).encode('utf-8')\n"+\
                "\t\t"+self.name.lower()+".data = json_dumps(post_content)\n"+\
                "\t\t"+self.name.lower()+".save()\n"+\
                "\t\treturn "+self.name.lower()
                
            else:
                self.model_save_function_body += \
                "\t\t\t"+self.name.lower()+" = blogging.models.Section.objects.get(id=self.id)\n"+\
                "\t\telse:\n"+\
                "\t\t\t"+self.name.lower()+" = blogging.models.Section()\n"
        
        if self.is_leaf:
            self.model_name = 'class '+ str(self.name).capitalize()+'Model(blogging.models.Content)'
        else:
            self.model_name = 'class '+ str(self.name).capitalize()+'Model(blogging.models.Section)'
        
        #Create entries for each new content field
        #Add PID count implicitly
        self.model_member_string_list.append('\tpid_count = models.PositiveIntegerField(blank=True)\n')
        for member_name, member_type in self.member_dict.iteritems():
            if str(member_type) == 'TextField':
                class_member = '\t'+member_name+'=\tmodels.TextField() \n'
            elif str(member_type) == 'CharField':
                class_member = '\t'+member_name+'=\tmodels.CharField(max_length = 100) \n'
            self.model_member_string_list.append(class_member)
            
            #Pop custom members if passed into init
            self.model_initfunction_pre_super_string += \
                '\t\tif '+member_name+' in kwargs:\n'+\
                '\t\t\t'+member_name.lower()+'= kwargs.pop("'+member_name+'")\n'+\
                '\t\telse:\n'+\
                '\t\t\t'+member_name.lower()+'= None\n'
            
            #Put custom members back into init
            self.model_initfunction_post_super_string += \
                '\t\tself.'+member_name+' = '+ member_name.lower()
        
        create_init()
        create_save()

    def create_rest_serializer(self):
        pass

    
    def form_string(self):
        
        final_string =  self.import_string + self.file_start + self.form_name
        for member in self.form_member_string_list:
            #print final_string
            final_string += member

        final_string += self.form_initfunction_string + self.class_formclass_save_string
        
        return final_string
    

class CreateTemplate():
    """
    This class will auto generate the template to be used for Detail page of that content type object
    """
    def __init__(self, name, member_dict,is_leaf):
        self.start_string = '{% extends "blogging/test_detail.html" %}\n'
        self.start_string += '\t{% block custom_detail %}\n'
        self.start_string += '\t\t{% autoescape off %}\n'
        self.member_list = []
        self.end_string = '\t\t{% endautoescape %}\n\t{% endblock %}\n'
        for member_name, member_type in member_dict.iteritems():
            member_string = '\n\t\t\t{{ content.' + member_name + ' }}\n'
            self.member_list.append(member_string)
    
    def form_string(self):
        final_string = self.start_string 
        for member in self.member_list:
            final_string += member
        final_string += self.end_string
        return final_string 
          


def test_fun():
    name = 'basecontent'
    member_dict = {'title': 'TextField',
                   'content': 'TextArea',
                   'Author' : 'TextField'
                   }
    
    create_class = CreateClass(name,member_dict)
    
    string =  create_class.form_string()
    print string
