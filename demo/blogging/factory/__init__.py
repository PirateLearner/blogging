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

def serializer_field_expand(value):
    field = serializer_typemap[value]
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

restrict_output_for = ['data'] # :( I didn't want to get specific

from blogging.rest.serializers import ManageSerializer, ContentSerializer

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
    def get_serializer_name(cls, name):
        return cls.sanitize_name(name)+"Serializer"
    
    @classmethod
    def get_manage_serializer_name(cls, name):
        return "Manage"+cls.get_serializer_name(name)
    
    @classmethod
    def get_view_serializer_name(cls, name):
        return "View"+cls.get_serializer_name(name)
    
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
        text = "\n"+"from django.db import models\n"
        text += "from blogging.models import (AbstractContent, Content)\n"
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
        text += "  "*indent+"data=kwargs.get('data', None)\n"+\
                "  "*indent+"if data is not None:\n"+\
                "   "*indent+"data = json.loads(data)\n"+\
                "   "*indent+"self.pid_count = data.get('pid_count', None)\n"+\
                "   "*indent+"self.id = kwargs.get('id', None)\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "   "*indent + "self."+ key.lower() +" = data.get('" +\
                                                        key.lower()+"',None)\n"
        text += "  "*indent+"else:\n"
        text += "   "*indent + "self.pid_count = pid_count\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "   "*indent + "self."+ key.lower() +" = " + \
                                                            key.lower()+"\n"
        text += "  "*indent+"delattr(self, 'data')\n"
        text += "  "*indent+"delattr(self, 'objects')\n"
        
        text += "\n"
        return text
    
    def create_form_block(self):
        pass
    
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
                "json.loads(obj.data).get('"+key.lower()+"', None))"
        return text
    
    def create_content_serializer_block(self, indent=0):
        serial_name = self.get_serializer_name(self.name)
        text = "\n"+"class View"+serial_name+"(ContentSerializer):\n"
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
                        serializer_field_expand(value['type'])+")"
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
        text += "  "*indent+"exclude=("
        for member in restrict_output_for:
            text += "'"+member+"',"
        text += ")\n"
        text += "  "*indent+"extra_kwargs = "+\
                ContentSerializer.Meta.extra_kwargs.__str__()
        text += "\n"
        
        #Getters
        for member in self.members:
            for key,value in member.items():
                if key.lower() not in reserved_keywords:
                    text += "\n"
                    text += " "*indent+"def get_"+key.lower()+"(self, obj):\n"
                    text += "  "*indent+"return json.loads(obj.data).get('"+\
                                         key.lower()+"', None)\n"

        return text

    def create_manage_serializer_block(self, indent=0):
        serial_name = self.get_serializer_name(self.name)
        text = "\n"+"class Manage"+serial_name+"(ManageSerializer):\n"
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
                        serializer_field_expand(value['type'])+")"
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
        text += "  "*indent+"exclude=("
        for member in restrict_output_for:
            text += "'"+member+"',"
        text += ")\n"
                    
        text += "  "*indent+"extra_kwargs = "+\
                    ManageSerializer.Meta.extra_kwargs.__str__()+"\n"

        #Getters
        for member in self.members:
            for key,value in member.items():
                if key.lower() not in reserved_keywords:
                    text += "\n"
                    text += " "*indent+"def get_"+key.lower()+"(self, obj):\n"
                    text += "  "*indent+"return json.loads(obj.data).get('"+\
                                         key.lower()+"', None)\n"
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
                    "validated_data['data'] = json.dumps(post_content)\n"
        text += "  "*indent+"return super().create(validated_data)\n"
        
        #Update Method
        text += "\n"+" "*indent+"def update(self, instance, validated_data):\n"
        text += "\n"+"  "*indent+"data = json.loads(instance.data)\n"
        text += "  "*indent+"post_content = {}\n" +\
                "  "*indent+"post_content['pid_count'] = "+\
                "data.get('pid_count', None)\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "  "*indent+"post_content['"+key.lower()+\
                            "'] = validated_data.pop('"+key.lower()+\
                            "', data.get('"+key.lower()+"', None))\n"
        text += "\n"
        text += "  "*indent+\
                    "validated_data['data'] = json.dumps(post_content)\n"
        text += "  "*indent+"return super().update(instance, validated_data)\n"
        return text
    
    def save(self):
        '''
        Write to disk:
        
        At this point, if we are overwriting, we actually meant to do so.
        '''
        file_path = self.get_full_file_path(self.get_file_name(self.name))
        fd = open(file_path, 'w')
        
        fd.write("raw_name = '"+self.name+"'\n")
        fd.write(self.create_model_imports())
        fd.write(self.create_model_block(indent=0))
        fd.write(self.create_serializer_imports())
        fd.write(self.create_content_serializer_block(indent=0))
        fd.write(self.create_manage_serializer_block(indent=0))
        
        fd.close()
#         print (self.name)
#         print (self.create_model_imports())
#         print (self.create_model_block(indent=0))
#         print (self.create_serializer_imports())
#         print (self.create_serializer_block(indent=0))