'''
Created on 10-May-2018

@author: anshul

@brief Library to generate code bindings for custom template types in the app.
'''
typemap = {
            'TextField': 'TextField',
            'CharField': 'CharField',
            'Image'    : 'ImageField',
           }

from blogging.models import AbstractContent
reserved_keywords = [field.name for field in AbstractContent._meta.get_fields()]

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
                                             typemap.get(value['type'])+"()\n"
        
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
        text = "\n" + "from rest_framework import serializers\n"
        text += "from django.template.defaultfilters import slugify\n"

        return text
        
    def create_serializer_block(self, indent=0):
        serial_name = self.get_serializer_name(self.name)
        text = "\n"+"class "+serial_name+"(serializers.ModelSerializer):\n"
        indent += 4
        
        #Meta class
        text += " "*indent+"class Meta:\n"
        text += "  "*indent+"model = "+self.get_model_name(self.name)+"\n"
        text += "  "*indent+"fields = ('id', 'title', 'create_date', "+\
                                                                "'author'"
        
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += ",\n"+"    "*indent+"'"+key.lower()+"'"
        text += ",)\n"
        text += "  "*indent+"extra_kwargs = {'author':{'required': False}}\n"
        #Create Method
        text += "\n"+" "*indent+"def create(self, validated_data):\n"
#         text += "  "*indent+"print('printing')\n"
#         text += "  "*indent+"for k,v in validated_data.items():"+\
#                 "   "*indent+"print(k, v)\n"
        text += "  "*indent+self.class_name.lower()+" = Content()\n"+\
                "  "*indent+self.class_name.lower()+".title = "+\
                                    "validated_data.get('title')\n"+\
                "  "*indent+self.class_name.lower()+".author = "+\
                                    "validated_data.get('author')\n"
        
        text += "\n"+"  "*indent+"post_content = {}\n" +\
                "  "*indent+"post_content['pid_count'] = "+\
                "validated_data.get('pid_count')\n"
        
        #text += "  "*indent +"fields = kwargs.pop('fields')\n"+\
        #        "  "*indent +"for field in fields:\n"+\
        #        "   "*indent +"post_content[field] = getattr(self, field)\n"
        for member in self.members:
            for key,value in member.items():
                if key in reserved_keywords:
                    continue
                text += "  "*indent +"post_content['"+key+"'] = "+\
                            "validated_data.get('"+key+"')\n"
                
        text += "\n"
        text += "  "*indent+self.class_name.lower()+".data = "+\
                                                  "json.dumps(post_content)\n"
        text += "  "*indent+self.class_name.lower()+".save()\n\n"
        text += "  "*indent+"return "+ self.class_name.lower()+"\n"
        
        #Update Method
        text += "\n"+" "*indent+"def update(self, instance, validated_data):\n"
        text += "  "*indent+"instance.title = validated_data.get("+\
                                                   "'title', instance.title)\n"
        text += "  "*indent+"instance.pid_count = validated_data.get("+\
                                           "'pid_count', instance.pid_count)\n"
        text += "  "*indent+"instance.author = validated_data.get("+\
                                            "'author', instance.author)\n"
        for member in self.members:
            for key,value in member.items():
                if key.lower() in reserved_keywords:
                    continue
                text += "  "*indent+"instance."+key.lower()+\
                            " = validated_data.get('"+key.lower()+\
                            "', instance."+key.lower()+")\n"
        text += "  "*indent+"instance."+"save()\n"
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
        fd.write(self.create_serializer_block(indent=0))
        
        fd.close()
#         print (self.name)
#         print (self.create_model_imports())
#         print (self.create_model_block(indent=0))
#         print (self.create_serializer_imports())
#         print (self.create_serializer_block(indent=0))