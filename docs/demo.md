Blogging App Demo Quick Start Guide
===================================

Created by [Pirate Learner](http://piratelearner.com)
-----------------------------------------------------

This is a sample project to demonstrate how to use the _Blogging_ app as a standard django package in you projects.

### Install Instructions

1. Create a virtual environment to test this app:

	```shell
	virtualenv testenv --no-site-packages
	source testenv/bin/activate
	``` 

2. Install the necessary packages from the supplied requirements file:

	```shell
	pip install -r requirements.txt
	```
3. Create the necessary tables:

	```shell
	python manage.py syncdb --all
	python manage.py createinitialrevisions
	```
	
	The wizard will prompt you to create a super user. Make one, for Sections can currently be created from the admin only.
	
4. Start the development server:

	```shell
	python manage.py runserver
	```
	
	This will take you to the default page where nothing has been created so far. You can start from scratch here, or could explore further 
	by installing the fixtures we've provided. Currently, a menu bar should be visible with quick links to 
	
	* Create Content Types - Where you can create parent sections and/or content types.
	* Contact page - Which demonstrates the use of contact template tag.
	
5. Install fixtures:
	
	Close the development server, and from within the virtual environment:
	```shell
	python manage.py loaddata fixtures.json
	```
	This will load the following:
	
	1. A Sample content type which is a non-leaf node _'Section'_. This _'section'_ has then been used to create parent sections, _'Articles'_ and _'Blog'_
	   __NOTE__ that _'Blog'_ section gets a special treatment currently, in a way that frontend creation of content into this section is disabled. 
	2. A sample content type _'Article'_ which is a leaf-node. This represents the content-type which is used to create actual, long text content, like articles
	and blog entries. Using this, we've created a sample post by the name _'I have a dream by Martin Luther King'_.
	
	(Please note that it is a little bit of a hack. We've shipped two premade python files in the custom folder, namely `article.py` and `section.py` in the `custom` folder.
	It is adviced that you remove those entries from DB first from the frontend, when using in a final project, which will delete the python files too, and start from scratch. 
	They are for demonstration purposes only.)
	
6. Start the development server:

	```shell
	python manage.py runserver
	```
	
	Now, you will see a few pre-created content samples when you visit the Blogging tab (By clicking on the menu).
	You must be looking at two panels going by the names a. _Blog_ and b. _Articles_
	
	Clicking on _'Articles'_ will take you to the teaser view of the article. Click on the URL to see the full page. 
	
	'Create Content' will not be visible until you log in. To log in, you could use the django-admin _http://127.0.0.1:8000/admin/_ URL.
	When you return, create content should be visible.
	
	To edit the post, click on the `Edit Post` link (visible only if logged in).
