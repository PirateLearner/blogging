# Templates and Views

Following templates and views are supported:

## Index View 

Index page of the app is in the tiled view of the top level blog parents. All the blog parents whose parents is null fall into this category. This views is facilitated by
the section.html template and user may change the layout of the index page by changing the html and css of this template. 

## Parent Views

Parent views are same as that of index view if the there exist atleast one child of that particular parent, othervise it will be viewed as stacked view. 
Non-Leaf parent view is drive by the section.html and will show all the parents node having that particular node as it's parent.
Leaf parent view is drived by the teaser.html template and will display all the blog article that have their parent as the requested node. 

__ Please note that the image visible in these tiled or stacked views are derived from either parent or blog post itself. Make sure that there is atleast one image in 
data section of parent and in blog article __

## Detail View

Blog article is displayed in the detail view and is drived by the detail.html template. This view also support the minimilistic view but that is only available to the 
logged-in user. These blog article can also be edited by just entring the url ` {article_url}?edit=True `. 

## Tagged articles view

Tagged article views is also support and will show all the article that have chosen tag. This is is also facilitated by the teaser.html and display all the tagged
article in stacked views. 

Following views are not supported as of now, but will be available for use in future versions:

* Author list.
* Author posts.
* Archived based on year.
* Archived based on month.
* Archived based on Day.
 