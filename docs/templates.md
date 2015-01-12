# Templates and Views

Following templates and views are supported:

## Index View 

This view will generate a thumnail view of all parents that exist. 
(So, we advice that you put at least one image in the description field, which the app will pick as the thumbnail. 
The first occurance of image will be used as thumbnail). If no image is found, the image of its immediate parent will be used. If it is the absolute parent...
well, we recommend you put an image.
Index page of the app is in the tiled view of the top level blog parents. 
All the blog parents whose parent is null fall into this category. 
From this page, one can navigate the section heirarchy (which ultimately ends at a detailed post).
This views is facilitated by the `section.html` template and user may change the layout of the index page by changing the html and css of this template.

## Parent Views

Parent views are same as that of index view if the there exist atleast one child of that particular parent, otherwise it will be viewed as stacked view. 
Non-Leaf parent view is driven by the `section.html` and will show all the parents node having that particular node as it's parent.
Leaf parent view is driven by the `teaser.html` template and will display all the articles that have their parent as the requested node. 

__ Please note that the image visible in these tiled or stacked views are derived from either parent or blog post itself. Make sure that there is atleast one image in 
data section of parent and in blog article __

## Detail View

Blog article is displayed in the detail view and is driven by the `detail.html` template. 
These blog article can also be edited by just entring the url ` {article_url}?edit=True `.
You can always create buttons out of these as is done in the working demo of this project. 

## Tagged articles view

Tagged article views is also supported and will show all the articles that have the chosen tag. 
This is is also facilitated by the `teaser.html` and display all the tagged article in stacked views. 

Following views are not supported as of now, but will be available for use in future versions:

* Author list.
* Author posts.
* Archived based on year.
* Archived based on month.
* Archived based on Day.
