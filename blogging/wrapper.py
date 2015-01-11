import re
import os
import importlib

def project_path():
    PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
    print PROJECT_PATH

def get_pattern(current_tag):
    tag_start_pattern = "\\%\\% " + str(current_tag['name']) + " \\%\\%"
    tag_end_pattern = "\\%\\% endtag "+ str(current_tag['name']) + " \\%\\%"
    final_pattern = tag_start_pattern + "(.*?)" + tag_end_pattern
    return final_pattern

def get_field_name_from_tag(current_tag):
    field_name = current_tag.split("_")[0:-1]
    return_name = "_".join(str(tag) for tag in field_name)
    return return_name
    
def parse_content(data, tag):
    final_pattern = get_pattern(tag)
    patt = re.compile(final_pattern)
    result = patt.search(data)
    return result.group(1)

def insert_tag_into_content(data,tag):
    tag_start = "\%\% " + str(tag["name"]) + " \%\%" 
    tag_end = "\%\% endtag " + str(tag["name"]) + " \%\%" 
    print type(data)
    print data
    return_field = tag_start + str(data) + tag_end
    print "rebuilding tags " + return_field
    return return_field
         
def find_class(module_name,class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c
