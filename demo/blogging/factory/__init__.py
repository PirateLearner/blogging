'''
Created on 10-May-2018

@author: anshul

@brief Library to generate code bindings for custom template types in the app.
'''
model_typemap = {
            'TextField': 'TextField',
            'CharField': 'CharField',
            'Image'    : 'ImageField',
           }

serializer_typemap = {
            'TextField': {'name':'CharField',
                          'extra': {
                                    'style':"{"+\
                                            "'base_template': 'textarea.html'"+\
                                            "}",
                                    },
                          },
            'CharField': {'name':'CharField',
                          'extra': None,
                          },
            'Image'    : {'name': 'ImageField',
                          'extra': None,
                          }
            }

form_typemap = {
            'TextField': {'name':'CharField',
                          'extra': None,
                          },
            'CharField': {'name':'CharField',
                          'extra': None,
                          },
            'Image'    : {'name': 'ImageField',
                          'extra': None,
                          }
            }
import os
def field_options_expand(value, dictionary = serializer_typemap):
    field = dictionary[value]
    #text = field.get('name')+'('
    text = ''
    if field.get('extra', None) is not None:
        for k,v in field.get('extra').items():
            text += k+" = " + v
    #text += ")"
    
    return text

from blogging.models import AbstractContent
reserved_keywords = [field.name for field in AbstractContent._meta.get_fields()]
reserved_keywords += ['pid_count']

restrict_output_for = ['text'] # :( I didn't want to get specific

from blogging.rest.serializers import ManageSerializer, ContentSerializer
from blogging.forms import ManageForm

class CreateTemplate(object):
    """
    Member is a list of dictionaries:
    [
     {
      'title': {'type': 'value',
                'extra': {...}},
     },
     {
      'body': {'type': 'value',
               'extra': {...}},
     },
    ] 
    """
    
    @classmethod
    def get_file_name(cls, name):
        return '_'.join(name.lower().split(' ')).strip()
    
    @classmethod
    def get_full_file_path(cls, name):
        from os import path
        return path.dirname(__file__)+"/../custom/"+cls.get_file_name(name)+".py"
    
    @classmethod
    def file_exists(cls, name):
        from os import path
        if path.isfile(cls.get_full_file_path(name)):
            return True
        return False

    @classmethod
    def backup_file(cls, name):
        from time import time
        name = cls.get_full_file_path(name)
        os.rename(name, name+'_'+str(time()))

    @classmethod
    def get_serializer_name(cls, name):
        return cls.sanitize_name(name)+"Serializer"
    
    @classmethod
    def get_manage_serializer_name(cls, name):
        return "Manage"+cls.get_serializer_name(name)
    
    @classmethod
    def get_view_serializer_name(cls, name):
        return "View"+cls.get_serializer_name(name)

    @classmethod
    def get_form_name(cls, name):
        return cls.sanitize_name(name)+"Form"
    
    @classmethod
    def sanitize_name(cls, name):
        return '_'.join(name.lower().title().split(' ')).strip()
    
    @classmethod
    def get_model_name(cls, name):
        return cls.sanitize_name(name)+"Model"
    
    
    def __init__(self, name, members):
        self.name = name
        self.members = members #Members is a list of dictionary items
        
        self.class_name = self.sanitize_name(name)
        self.file_name = self.get_file_name(self.name)
        
        
    def create_model_imports(self):
        #text = "\n"+"from django.db import models\n"
        text = "from blogging.models import (AbstractContent, Content)\n"
        text += "import json\n"
        
        return text
    
    def create_model_block(self, indent=0):
        model_name = self.get_model_name(self.name)
        text = "\n"+"class "+model_name+"(AbstractContent):\n"
        indent += 4
        text += " "*indent +\
                    "pid_count = models.PositiveIntegerField(blank=True)\n"
        for member in self.members:
            for key, value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += " "*indent +key.lower()+" = models."+\
                                     model_typemap.get(value['type'])+"()\n"
        
        #Constructor
        text += "\n" +" "*indent +\
                "def __init__(self, *args, **kwargs):\n"+\
                "  "*indent +"if 'pid_count' in kwargs:\n"+\
                "   "*indent + "pid_count = kwargs.pop('pid_count')\n"+\
                "  "*indent +"else:\n"+\
                "   "*indent + "pid_count = None\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "  "*indent +"if '"+ key +"' in kwargs:\n"+\
                        "   "*indent + key.lower()+" = kwargs.pop('"+key+"')\n"+\
                        "  "*indent +"else:\n"+\
                        "   "*indent + key.lower()+" = None\n"
        
        text += "  "*indent+"super("+model_name+\
                                        ", self).__init__(*args, **kwargs)\n"
        text += "  "*indent+"text=kwargs.get('text', None)\n"+\
                "  "*indent+"if text is not None:\n"+\
                "   "*indent+"text = json.loads(text)\n"+\
                "   "*indent+"self.pid_count = text.get('pid_count', None)\n"+\
                "   "*indent+"self.id = kwargs.get('id', None)\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "   "*indent + "self."+ key.lower() +" = text.get('" +\
                                                        key.lower()+"',None)\n"
        text += "  "*indent+"else:\n"
        text += "   "*indent + "self.pid_count = pid_count\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "   "*indent + "self."+ key.lower() +" = " + \
                                                            key.lower()+"\n"
        text += "  "*indent+"delattr(self, 'text')\n"
        text += "  "*indent+"delattr(self, 'objects')\n"
        
        text += "\n"
        return text
    
    def create_form_imports(self):
        text = "\nfrom django import forms\n"
        text += "\n"
        return text

    def create_form_block(self, indent = 0):
        form_name = self.get_form_name(self.name)
        text = "class "+form_name+"(forms.ModelForm):\n"
        indent += 4
        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += " "*indent + key.lower()+"= forms."+\
                        form_typemap[value['type']].get('name') +"("+\
                        field_options_expand(value['type'], 
                                             dictionary = form_typemap)+")\n"
                        
        text += "\n"+" "*indent + "class Meta:\n"
        text += "  "*indent +"model = Content\n"
        text += "  "*indent+"exclude="+str(ManageForm.Meta.exclude)+"+("
        for member in restrict_output_for:
            text += "'"+member+"',"
        text += ")+('author',)\n"
        
        #Enhance __init__ if data is provided, we need to do some field jugglery
        text += "\n"
        text +=" "*indent+"def __init__(self, *args, data=None, initial=None,"+\
                                " instance=None, **kwargs):\n"
        #If data is provided (saving form data?), create a 'text' field to 
        #create a model instance. It can be blank, we will be saving it eventually
        text += "  "*indent+"initial = {} if initial is None else initial\n"
        text +="  "*indent+"if data is not None:\n"+\
               "   "*indent+"data['text'] = ''\n"
        text += "  "*indent+"if instance is not None:\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "   "*indent+"initial['"+key.lower()+\
                        "'] = json.loads(instance.text).get('"+key.lower()+"', None)\n"
        text +="  "*indent+"super("+form_name+", self).__init__(*args, "+\
                    "data=data, instance=instance, initial=initial,"+\
                    "**kwargs)\n"
        
        #If instance was also provided (Updating stuff?))
        
        #Enhance save method
        text += "\n"
        text += " "*indent+"def save(self, *args, **kwargs):\n"
        text +="  "*indent+"post_content = {}\n"+\
               "  "*indent+"post_content['pid_count'] = None\n"
               
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "  "*indent+"try:\n"
                text += "   "*indent+"post_content['"+key.lower()+"']= "+\
                            "self.cleaned_data.get('"+key.lower()+"',"+\
                            " json.loads(self.instance.text).get('"+\
                            key.lower()+"'))\n"
                text += "  "*indent+"except:\n"
                #text += "   "*indent+"print('Exception')\n"
                text += "   "*indent+"post_content['"+key.lower()+"']= "+\
                            "self.cleaned_data.get('"+key.lower()+"',None)\n"
                            
        text += "  "*indent+"self.instance.text = json.dumps(post_content)\n"
        #text += "  "*indent+"print(self.instance.text)\n"
        text += "  "*indent+"return super().save(*args, **kwargs)"
        
        return text
        
    def create_serializer_imports(self):
        text = "\n" + "from rest_framework import serializers"
        text += "\n" + "from blogging.rest.serializers import "+\
                       "(ContentSerializer,"+\
                       "ManageSerializer)\n"
        text += "from django.template.defaultfilters import slugify\n"

        return text
    
    def create_serializer_field_block(self, key, value, indent=4):
        text = " "*indent + "class "+key.lower().title()+\
                "Field(serializers."+serializer_typemap[value['type']].get('name')+"):\n"
        text +="  "*indent+"def get_attribute(self, obj):\n"+\
               "   "*indent+"return ("+\
                "json.loads(obj.text).get('"+key.lower()+"', None))"
        return text
    
    def create_content_serializer_block(self, indent=0):
        text = "\n"+"class "+self.get_view_serializer_name(self.name)+\
                                                    "(ContentSerializer):\n"
        indent += 4
        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += self.create_serializer_field_block(key, value, indent)
                
        text += "\n"
        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "\n"+" "*indent+key.lower()+"= "+\
                        key.lower().title()+"Field("+\
                        field_options_expand(value['type'])+")"
        text += "\n"
        
        for member in restrict_output_for:
            text +=" "*indent+member+"=None\n"
            
        #Meta class
        text += "\n"+ " "*indent+"class Meta:\n"
        #text += "  "*indent+"model = "+self.get_model_name(self.name)+"\n"
        text += "  "*indent+"model = Content\n"
#         text += "  "*indent+\
#                 "fields = " + ContentSerializer.Meta.fields.__str__()+ "+("
#                 
#         for member in self.members:
#             for key,value in member.items():
#                 if key.lower() in reserved_keywords:
#                     continue
#                 text += "\n"+"     "*indent+"'"+key.lower()+"',"
#         text += ")\n"
        
        #text += "  "*indent+"fields= '__all__'\n"
        text += "  "*indent+"exclude="+str(ContentSerializer.Meta.exclude)+"+("
        for member in restrict_output_for:
            text += "'"+member+"',"
        text += ")\n"
        text += "  "*indent+"extra_kwargs = "+\
                ContentSerializer.Meta.extra_kwargs.__str__()
        text += "\n"
        
        #Getters
#         for member in self.members:
#             for key,value in member.items():
#                 if key.lower() not in reserved_keywords:
#                     text += "\n"
#                     text += " "*indent+"def get_"+key.lower()+"(self, obj):\n"
#                     text += "  "*indent+"return json.loads(obj.text).get('"+\
#                                          key.lower()+"', None)\n"

        return text

    def create_manage_serializer_block(self, indent=0):
        text = "\n"+"class "+self.get_manage_serializer_name(self.name)+\
                                                    "(ManageSerializer):\n"
        indent += 4
        
        #text += " "*indent+"template = serializers.PrimaryKeyRelatedField("+\
        #                "queryset = Template.objects.all(), required=False)"        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += self.create_serializer_field_block(key, value, indent)
                
        text += "\n"
        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "\n"+" "*indent+key.lower()+"= "+\
                        key.lower().title()+"Field("+\
                        field_options_expand(value['type'])+")"
        text += "\n"
        
        for member in restrict_output_for:
            text +=" "*indent+member+"=None\n"
            
        #Meta class
        text += "\n"+ " "*indent+"class Meta:\n"
        #text += "  "*indent+"model = "+self.get_model_name(self.name)+"\n"
        text += "  "*indent+"model = Content\n"
#         text += "  "*indent+\
#                 "fields = " + ManageSerializer.Meta.fields.__str__()+ "+("
#         for member in self.members:
#             for key,value in member.items():
#                 if key.lower() in reserved_keywords:
#                     continue
#                 text += "\n"+"     "*indent+"'"+key.lower()+"',"
#         text += ")\n"
        
        #text += "  "*indent+"fields= '__all__'\n"
        text += "  "*indent+"exclude="+str(ManageSerializer.Meta.exclude)+"+("
        for member in restrict_output_for:
            text += "'"+member+"',"
        text += ")\n"
                    
        text += "  "*indent+"extra_kwargs = "+\
                    ManageSerializer.Meta.extra_kwargs.__str__()+"\n"

#         #Getters
#         for member in self.members:
#             for key,value in member.items():
#                 if key.lower() not in reserved_keywords:
#                     text += "\n"
#                     text += " "*indent+"def get_"+key.lower()+"(self, obj):\n"
#                     text += "  "*indent+"return json.loads(obj.text).get('"+\
#                                          key.lower()+"', None)\n"
        #Create Method
        text += "\n"+" "*indent+"def create(self, validated_data):\n"
        text += "\n"+"  "*indent+"post_content = {}\n" +\
                "  "*indent+"post_content['pid_count'] = None\n"
        
        for member in self.members:
            for key,value in member.items():
                if key in reserved_keywords:
                    continue
                text += "  "*indent +"post_content['"+key+"'] = "+\
                            "validated_data.pop('"+key+"')\n"
        text += "\n"
        text += "  "*indent+\
                    "validated_data['text'] = json.dumps(post_content)\n"
        text += "  "*indent+"return super().create(validated_data)\n"
        
        #Update Method
        text += "\n"+" "*indent+"def update(self, instance, validated_data):\n"
        text += "\n"+"  "*indent+"try:"
        text += "\n"+"   "*indent+"text = json.loads(instance.text)"
        text += "\n"+"  "*indent+"except:"
        text += "\n"+"   "*indent+"text = {}\n"
        text += "  "*indent+"post_content = {}\n" +\
                "  "*indent+"post_content['pid_count'] = "+\
                "text.get('pid_count', None)\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "  "*indent+"post_content['"+key.lower()+\
                            "'] = validated_data.pop('"+key.lower()+\
                            "', text.get('"+key.lower()+"', None))\n"
        text += "\n"
        text += "  "*indent+\
                    "validated_data['text'] = json.dumps(post_content)\n"
        text += "  "*indent+"return super().update(instance, validated_data)\n"
        return text
    
    def create_render_block(self):
        indent = 0
        text = '\n\ndef render(text=None):\n'
        indent +=4
        
        text += ' '*indent+"if text is None:\n"
        indent +=4
        text += ' '*indent+"return ''\n"
        indent -=4
        text += ' '*indent+"rendered_text = ''\n"
        
        text += ' '*indent+"try:\n"
        indent +=4
        text += ' '*indent+"text = json.loads(text)\n"+\
                ' '*indent+"for next in ordered_members:\n"
        indent +=4
        text += ' '*indent+"rendered_text += text[next]\n"
        indent -=4
        
        indent -= 4
        text += ' '*indent+"except:\n"
        text += '  '*indent+'pass\n'
        
        text += ' '*indent+'return rendered_text'
        return text
    
    def create_list_of_members(self):
        '''
        Create an ordered list of members as the user placed them
        '''
        text = '['
        for member in self.members:
            for key, value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "'"+key.lower()+"',"
        text += ']'
        return text
    
    def save(self):
        '''
        Write to disk:
        
        At this point, if we are overwriting, we actually meant to do so.
        '''
        file_path = self.get_full_file_path(self.get_file_name(self.name))

        try:
            if( self.file_exists(self.name)):
                self.backup_file(self.name)
            fd = open(file_path, 'w')
            
            fd.write("raw_name = '"+self.name+"'\n")
            fd.write("ordered_members = "+ self.create_list_of_members()+'\n')
            fd.write(self.create_model_imports())
            #fd.write(self.create_model_block(indent=0))
            fd.write(self.create_serializer_imports())
            fd.write(self.create_content_serializer_block(indent=0))
            fd.write(self.create_manage_serializer_block(indent=0))
            
            fd.write(self.create_form_imports())
            fd.write(self.create_form_block(indent=0))
            fd.write(self.create_render_block())
            fd.close()
            return True
        except:
            if CreateTemplate.file_exists(self.name):
                os.remove(file_path)
            return False
#         print (self.name)
#         print (self.create_model_imports())
#         print (self.create_model_block(indent=0))
#         print (self.create_serializer_imports())
#         print (self.create_serializer_block(indent=0))