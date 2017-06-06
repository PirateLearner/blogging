from events.decorators import register_handle
from events.models import send
from django.contrib.contenttypes.models import ContentType

@register_handle("blogging_content_submit")
def handle_submit_event(sender, *args,**kwargs):
    """
    On submit event send the Mail to Group Administrator 
    """
    
    user = kwargs.get("user",None)
    label = kwargs.get("event_label",None)
    source_content_type = kwargs.get("source_content_type",None)
    source_object_id = kwargs.get("source_object_id",None)

    if label is None:
        label = args[0]

    if user is None:
        user = args[1]

    if source_content_type is None:
        source_content_type = args[2]

    if source_object_id is None:
        source_object_id = args[3]
        
    # get object from content type
    obj = source_content_type.get_object_for_this_type(pk=source_object_id)
    
    ## send the mails create Notice
#     notice = "Your Article {0} has been submitted for Review.".format(obj.get_menu_title())
#     extra_context = { "notice": notice, "subject": "Article submitted"}
#     template_name = "events/notifications/{0}/author.html".format(label)
#     
#     ret  = send([user],label,extra_context = extra_context, html=True, template_name=template_name)
#     print "Send to user return ", ret
    
    notice = "An article has been submitted for review. Please find the details as follows:"
    extra_context = { "notice": notice, "subject": "submitted for review", "author":user.profile.get_name(),"summary":obj.get_summary(),
                     "title": obj.get_menu_title(), "blog_url":obj.get_absolute_url()}
    template_name = "events/notifications/{0}/admin.html".format(label)
    ret  = send("Administrator",label,extra_context = extra_context, html=True, template_name=template_name)
    print "Send to Admistrator return ", ret
    

@register_handle("blogging_content_publish")
def handle_publish_event(sender, *args,**kwargs):
    """
    On publish event send the Mail to user 
    """
    
    user = kwargs.get("user",None)
    label = kwargs.get("event_label",None)
    source_content_type = kwargs.get("source_content_type",None)
    source_object_id = kwargs.get("source_object_id",None)

    if label is None:
        label = args[0]

    if user is None:
        user = args[1]

    if source_content_type is None:
        source_content_type = args[2]

    if source_object_id is None:
        source_object_id = args[3]
        
    # get object from content type
    obj = source_content_type.get_object_for_this_type(pk=source_object_id)
    
    ## send the mails create Notice
    extra_context = { "blog": obj, "subject": "Article published"}
    template_name = "events/notifications/{0}/author.html".format(label)
     
    ret  = send([user],label,extra_context = extra_context, html=True, template_name=template_name)
    print "Send to user return ", ret

    
