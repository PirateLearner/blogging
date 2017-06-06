from blogging.tag_lib import parse_content
from blogging.models import BlogContent, BlogParent, BlogContentType
import json
import os


def convert_tags(blog,tag_name,fd):
    tag = {}
#     tag['name'] = tag_name + '_tag'
    tag['name'] = tag_name
    content = parse_content(blog,tag)
    if len(content) > 0:
        fd.write("\nConverting "+ blog.title + "\n")
        tmp = {}
#         tmp[tag_name] = content
        tmp['content'] = content
        tag['name'] = 'pid_count_tag'
        content = parse_content(blog,tag)           
        if len(content) > 0:
            tmp['pid_count'] = content
        else:
            tmp['pid_count'] = '0'
        fd.write(json.dumps(tmp) + "\n\n")
        blog.data = json.dumps(tmp)
        return True
    else:
        return False



def migrate():
    blogs = BlogParent.objects.all()
    content_type = BlogContentType.objects.get(content_type='DefaultSection')
    form_filename = os.path.abspath(os.path.dirname(__file__))+"/custom/"+"migrate_sections.txt"
    fd = os.fdopen(os.open(form_filename,os.O_CREAT| os.O_RDWR , 0555),'w')
    
    for blog in blogs:

        if(convert_tags(blog, 'Body', fd)):
            blog.content_type = content_type 
            blog.save()
            continue
        elif (convert_tags(blog, 'content', fd)):
            blog.content_type = content_type
            blog.save()
            continue
        elif(convert_tags(blog, 'Content', fd)):
            blog.content_type = content_type
            blog.save()
            continue
        elif(convert_tags(blog, 'Summary', fd)):
            blog.content_type = content_type
            blog.save()
            continue
        elif(convert_tags(blog, 'Preface', fd)):
            blog.content_type = content_type
            blog.save()
            continue        
        else:
            print "NO TAGs FOUND in " + blog.title
            tmp = {}
            tmp['content'] = blog.data
            tmp['pid_count'] = '0'
            fd.write("\nAdding "+ blog.title + "\n")
            fd.write(json.dumps(tmp) + "\n\n")
            blog.data = json.dumps(tmp)
            blog.content_type = content_type
            print " Going to save " , blog , blog.content_type
            blog.save()
    fd.close()
            
if __name__ == "__main__":
    migrate()
        