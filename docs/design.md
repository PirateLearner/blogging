## Blogging App Design Documentation

This document records the design flow of the blogging app and the decisions for having such a design.

At the very outset, the blogging app provides for:
- Creation of blog posts.
	- Create
	- Edit
	- Delete
- Creation of categories/sections and subsections.
	- Create
	- Edit
	- Delete
- Viewing of a blogroll by:
	- Date
	- Section
- Viewing of individual posts.
- Viewing description of sections.

This can be done via both POST and RESTful APIs.

Models:

BlogContent:
- Title of Post
- Creation Date
- Last Modified Date
- Author
- Raw Data in post
- Is it published or not
- Does it have special Policies enabled on it?
- URL Path to post
- Section that it belongs to
- Content Type: Describes the way the content is to be formatted.
- Slug of title
- Tags
- When was it published?

TODO: Consider splitting the table into two. One contains statistical information, other contains configuration info.

What we would like to have here is that the user is able to change the way he creates content. 

Say, the user wants to create a blog post. So, he will need a title for that. Other than that, he'd ask for something like 'body' of the blogpost.
Maybe, he wants to have a 'summary' field too. Perhaps, he wants to add an image for that in a separate field.

Ideally, the user should be given the liberty of placing things as and where he likes. So, we need something like in place editing and drawing.
But, there is a flip side to that. If the app is in use by, say, a community, and they want to enforce certain conventions of layout for particular
types of post, then the user shouldn't be able to do as he/she pleases, but add things in a prescribed format.
So, in one place we have one time layout definiton and multiple reuse, and on the other hand, we have free flowing content everytime.

This could possibly be incorporated by the use of templates for editing. The trouble with the freestyled layouts is that the CSS won't be updated when the overall site layouts evolve unless we have a generic placement encoding accompanying the content and style is applied on the fly. (I like that idea!)

For now, let us focus on getting at par with the current design.


class Layout:
Only defines the way user can input data. This is new to the existing design. The user describes the layout format in which data must be entered or is accessed.

This is different from the previous design. We now decouple the way data is entered from the table it ultimately goes to. So, a section as well as an article may both use the same content layout, but still be stored in two different tables (because a section can have sub-sections, but an article cannot have more child articles.)

There is some trouble in visualizing how to have multiple hierarchies (or the need for them). Say, for example, we have sections. So, an article may belong to a 'Section' called 'blog'. An article could also belong to a 'Section' called 'Programming'. However, can an article belong to more than one section? Perhaps not. OK. Say, we define another hierarchy, 'Book'. Now, can an article belong to some 'Section' and also be part of a 'Book'? Why not! Then, what is the difference between a 'Book' and a new 'Section' which goes by the name 'Book' and does not have any parent (i.e. is the root? 

So, we'll simplify the notation. The class BlogParent is simply renamed to 'Section', similarly, 'BlogContent' is renamed to 'Content'. Also, as django has it, the app name would be prefixed to them, so DB will not have any ambiguity.

### Question
Can a section name be repeated, if it is contained within a different parent? For now, it is supposed to be unique, but is that justified?
For example, when sections are subject names, then each section may have a subsection on 'solved examples'. So, how do we resolve this requirement?
Perhaps, we can have tuple uniqueness for the section name and its parent. So, no section name may be repeated at the sibling level.

### Question
If a section is deleted, what happens to its content?

In the current implementation, DB was set to cascade. Thus, content is lost if parent section is deleted. This seems unreasonable. So, instead of that, we'll allow the content to reside without a section.

So, a NULL section is allowed in DB (it may be restricted on the front end), and if a section is deleted, its content's Section gets set to NULL.
