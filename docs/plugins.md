# CMS Plugins

Blogging app provide following plugins that can be used in Django-CMS:

## Latest Entries Plugin

This plugin displays the chosen number of latest blog articles in the plugin area and have following options to choose from:

* Base Parent (all the articles having this parent or its descendants as parent will be shown *Optional*).
* Number of entries (Number of entries to be shown).
* Tag filter ( etries will be filtered based on the tag *Optional*).
* Template (options for display of articles currently supported options - Teaser view,section view, Stacked List and Text List).

## Section Plugin

This plugin displays the chosen number of blog parents in the plugin area and have the following options to choose from:

* Base Parent (all the article blog parents having this or its descendants as parent wiil be shown *Optional*). 
* Number of nodes (Number of entries to be shown).

## Contact Plugin

This plugin will display the contact form in the plugin area and will send the e-mail to the admins specified in your project settings.py file. 
User may change the form fields and contents of e-mail in the `forms.py` and `cms_plugins.py` files respectively.
Current supported fields are-

* contact_type (*Mandatory*).
* Name 		   (*Mandatory*).
* email		   (*Mandatory*).
* content	   (*Mandatory*).
* extra 	   (*for human authentication*).
