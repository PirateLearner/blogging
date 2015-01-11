import re

from bs4 import BeautifulSoup


def get_field_name_from_tag(current_tag):
    field_name = current_tag.split("_")[0:-1]
    return_name = "_".join(str(tag) for tag in field_name)
    return return_name


def get_pattern(current_tag):
    tag_start_pattern = "\\%\\% " + str(current_tag['name']) + " \\%\\%"
    tag_end_pattern = "\\%\\% endtag "+ str(current_tag['name']) + " \\%\\%"
    final_pattern =  tag_start_pattern + "(.*?)" + tag_end_pattern 
    return final_pattern


def parse_content(db_object, tag):
    if str(tag['name']) == 'title_tag':
        return db_object.title
    final_pattern = get_pattern(tag)
    print "pattern to be found ", final_pattern
    ## DOTALL flag for including new line also
    patt = re.compile(final_pattern,flags=re.DOTALL)
    print "pattern  ", patt

#     print "data ", db_object.data
    result = patt.search(db_object.data)
#     print result
    return result.group(1)

def strip_tag_from_data(data):
    p = re.compile('\\%\\% .*? \\%\\%',flags=re.DOTALL)
    print "LOGS:: Stripping tags from data"
    line = p.sub('', data)
    return line

    
def has_no_id(tag):
    
    print "tag return has no id ", tag.has_attr('id')
    return  not tag.has_attr('id')



def has_enough_length(tag):
    """
    check for tag.string --> if it is None then it has more than one children.
    """
    print "has_enough_length()-->", tag.name
    
    if tag.string is None:
        tag_string = ''.join(str(tag_child) for tag_child in tag.contents)
        print "Printing contents string ", tag_string 
        flag = len(tag_string) > 100
        print "returning ", flag
        return flag
    else:
        print "Printing string ", tag.string
        flag = len(tag.string) > 100
        print "returning ", flag
        return flag
#     
#     
#     try:
#         contents = ''.join(tag.contents)
#         if contents is not None:
#             print contents
#             print "In li contents ", len(contents)
#             return len(contents) > 100
#         else:
#             return False
#     except:
#         
#         try:
#             if tag.string is not None:
#                 print tag.string
#                 print "In li String", len(tag.string)
#                 return len(tag.string) > 100
#             else:
#                 return False
#         except:
#             return False

def has_eligible_child(tag):
    for tag_child in tag.contents:
        if has_enough_length(tag_child):
            return True
    return False

def insert_tag_id(data,id_count):
    """
    
    Search for all children of body tag:
    1. if it is <p> then check for id, set it if not present.
    2. if it is <ul> or <ol> traverse through its children.
        a) if length of <li> is greater then 100 then set the id.
        b) if none of the <li> is suitable for id then give its parent the id.
    3. if it is <img> then set the id.
    
    Each set operation --> increament the pid_count and then set it to id field
    return the dictionary containing content and final pid_count
    
    soup = BeautifulSoup('<p id="1" style="text-align:justify"><span style="font-size:14px"><span style="font-family:comic sans ms,cursive">A day comes in the life of every programmer when they have to refactor someone else&#39;s code, or their own code, or fix a bug (heck, programmers spend a lot of time debugging someone else&#39;s crap as far as I know) and all hell breaks loose while deadlines tighten their noose around the&nbsp;neck. Here are a few simple practices that one can put to use in order to ease much of the future&nbsp;pain. They&#39;re not specific to any programming language, but generalizations which help keep things clean and less cluttered. They WILL not eliminate all your problems, but assuage it a bit, or perhaps a lot.</span></span></p> \
<ul> <li id="2" style="text-align:center"><span style="font-family:comic sans ms,cursive"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px">When writing an interface, method, function or any boundary to a block (a small system),&nbsp;<span style="font-size:16px"><strong>never trust anybody</strong>;</span> not even the future you, or the past you. Simply, don&#39;t assume. There will always be somebody who will disobey interface specifications, if one exists.&nbsp;We all have bad days. <span style="font-size:16px"><em><strong>Always, always, always check data consistency.</strong></em></span></span><br /> \
    <span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><img alt="" src="/static/media/images/2014/06/22/buy-sell.jpg" style="height:589px; width:640px" /></span><br />     <span style="color:rgba(0, 0, 0, 0.8); font-size:14px">(<a href="http://socks-studio.com/img/blog/buy-sell.jpg" target="_blank">Image Source</a>)</span></span></li> \
    <li id="4"style="text-align:center"><span style="font-family:comic sans ms,cursive"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><span style="font-size:16px"><strong>Document heavily</strong>. </span>No matter if it is absurd, no matter if you&#39;re writing just for yourself, not even if your documentation becomes the butt of meme jokes. Tell yourself what you are doing. <span style="font-size:16px"><strong>Know what you are doing</strong></span> (isn&#39;t that an oxymoron?). Write a symphony, tell a story. Murphy says that an issue will arise the moment you&#39;ve let the memory of the code recede. Murphy did not explicitly say that, but I&#39;m not saying that Murphy did not say that either.&nbsp;</span><br /> \
    <span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><img alt="" src="/static/media/images/2014/06/22/seuss_refactoring.jpg" style="height:443px; width:319px" /></span><br />     <span style="color:rgba(0, 0, 0, 0.8); font-size:14px">(<a href="http://s3.amazonaws.com/giles/092309/uyapgaukdqijirafwmpfwfcww.jpg" target="_blank">Image Credits</a>)</span></span></li> \
    <li id="5" style="text-align:center"><span style="font-family:comic sans ms,cursive"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><em><strong><span style="font-size:16px">Take what you need, not what you want.</span></strong></em> Especially C coders, I know boilerplate is fun and all, but in the end, if you wanted just the rose, and an elephant came along, holding it in his trunk, you might not satisfy the dependencies. Don&#39;t just include the stdio.h if you will never use it (okay, I&#39;m kidding, you may include it, if you know what you are doing). Besides, you do need a minimal boilerplate in web-design till the point you can make your own.</span><br /> \
    <span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><img alt="" src="/static/media/images/2014/06/22/boilderplatecode-300x284.jpg" style="height:284px; width:300px" /></span><br />     <span style="color:rgba(0, 0, 0, 0.8); font-size:14px">(<a href="https://dublin.zhaw.ch/~stdm/wp-content/uploads/2013/04/BoilderPlateCode.jpg" target="_blank">Image Source</a>)</span></span></li> \
    <li id="6" style="text-align:center"><span style="font-family:comic sans ms,cursive"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px">Don&#39;t modularize if a monolith would work. Provided you know what you are doing, always start with a whole, then, depending on the complexity and code reuse factors, break it into smaller reusable wholes. <em><strong><span style="font-size:16px">&quot;</span></strong><span style="font-size:16px"><em><strong>Premature optimization is the root of all evil&quot;</strong></em>.</span></em> Don&#39;t distribute until it starts to become unmanageable. Don&#39;t hold back distribution thinking you can handle anything.</span><br /> \
    <img alt="" src="/static/media/images/2014/06/22/engineers-boat.jpg" style="height:384px; width:417px" /><br /> <span style="font-size:12px">(<a href="http://aestheticblasphemy.com/philosophy/root-all-evil" target="_blank">Image Source</a>)</span></span></li> \
    <li id="7" style="text-align:center"><span style="font-family:comic sans ms,cursive"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px">To take care of the above step more effectively, <span style="font-size:16px"><strong>do it on paper first</strong></span> - a pseudo code, verbose descriptions, essays, anything that you are comfortable. Achieve it on paper first (or a notepad) and touch the code screen only when you know what you are going to do it, and how. It has the advantage that design comes first, supporting code comes later, so you&#39;ll see the patterns and methods more clearly. As it goes </span><em><span style="font-size:16px"><strong>&quot;Design is the first sign of human intention&quot;</strong></span>.&nbsp;</em><span style="color:rgba(0, 0, 0, 0.8); font-size:14px">Or else, be prepared to run in circles and come out squares (I don&#39;t know what that means actually).&nbsp;</span><br />\
    <span style="color:rgba(0, 0, 0, 0.8); font-size:14px"><img alt="" src="/static/media/images/2014/06/22/brain_to_paper.jpg" style="height:366px; width:500px" /></span><br />     <a href="http://3.bp.blogspot.com/-W4ICYhq1Alo/TbRtBtQi_3I/AAAAAAAAB8U/U18XywweeFU/s400/tumblr_lbu3munx6L1qzt15co1_400_large.jpg" target="_blank"><span style="color:rgba(0, 0, 0, 0.8); font-size:14px">(Image Source)</span></a></span></li> \
</ul> <p id="3" style="text-align:justify"><span style="font-size:14px"><span style="font-family:comic sans ms,cursive">&nbsp;But even after all of this, let it be clear that Software Development Cycle will never cease. You <strong>WILL </strong>have to refactor, there <strong>WILL </strong>be bugs, or feature requests, and you <strong>WILL </strong>have to modify your code. It is called evolution in Darwinian terms, it isn&#39;t meant to be perfect in the first shot, but should be robust and easy to evolve in the long shot. OOPs has &#39;ease of evolution&#39; as one of its core philosophies.</span></span></p> \
<p style="text-align:justify"><span style="font-size:14px"><span style="font-family:comic sans ms,cursive">&nbsp;But even after all of this, let it be clear that Software Development Cycle will never cease. You <strong>WILL </strong>have to refactor, there <strong>WILL </strong>be bugs, or feature requests, and you <strong>WILL </strong>have to modify your code. It is called evolution in Darwinian terms, it isn&#39;t meant to be perfect in the first shot, but should be robust and easy to evolve in the long shot. OOPs has &#39;ease of evolution&#39; as one of its core philosophies.</span></span></p>')
    """

    
#    print soup.body.contents

    filter_elements = ['p','span','img']

    print "Entering Soup"
    soup = BeautifulSoup(data)

    print "printing original html "
    initial_content = ''.join(str(tag) for tag in soup.body.contents)
    initial_content = initial_content.replace('\xc2\xa0', ' ')
    print initial_content

    
    for tag in soup.body.children:
        
        if tag.name == 'p' and has_no_id(tag):
            print "setting tag p"
            id_count = id_count + 1
            tag['id'] = id_count 

        elif (tag.name == 'ul' or tag.name == 'ol') and has_no_id(tag):
            if has_eligible_child(tag) == True:
                for tag_child in tag.contents:
                    if tag_child.name == 'li' and has_no_id(tag_child):
                        print "setting tag ",tag_child.name 
                        id_count = id_count + 1
                        tag_child['id'] = id_count 
            else:
                print "setting tag ", tag.name
                id_count = id_count + 1
                tag['id'] =  id_count
        elif tag.name == 'img' and has_no_id(tag):
            id_count = id_count + 1
            tag['id'] = id_count
            
            
    for tag_child in soup.body.descendants:
        
        if tag_child.name in filter_elements:
            tag_child['style'] = " "

        
    print "Now printing altered html "
    final_content = ''.join(str(tag) for tag in soup.body.contents)
    final_content = final_content.replace('\xc2\xa0', ' ')
    print final_content
    
    return_dict = {}
    return_dict['content'] = final_content
    return_dict['pid_count'] = id_count 
    
    return return_dict
